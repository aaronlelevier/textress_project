import calendar
import datetime
import pytz

from django.db import models
from django.db.models import Max, Sum
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from main.models import Hotel
from utils.exceptions import RechargeFailedExcp, AutoRechargeOffExcp


class Dates(object):

    tzinfo = pytz.timezone(settings.TIME_ZONE)

    @property
    def _now(self):
        return timezone.now()

    @property
    def _today(self):
        return self._now.date()

    @property
    def _year(self):
        return self._now.year

    @property
    def _month(self):
        return self._now.month

    def first_of_month(self, month=None, year=None):    
        """
        Return a timezone aware ``first_of_month`` datetime object. If no 
        ``month`` or ``year`` are given, return for the current month.
        """
        if not all([month, year]):
            month = self._today.month
            year = self._today.year

        return datetime.datetime(day=1, year=year, month=month,
            tzinfo=self.tzinfo).date()

    def last_month_end(self, date=None):
        "Return the last month's ending date as a `date`."
        date = date or self._today
        return self.first_of_month(month=date.month,
            year=date.year) - datetime.timedelta(days=1)


class AbstractBase(Dates, models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


###########
# PRICING #
###########

class PricingManager(models.Manager):

    def get_cost(self, units, units_mtd=0):
        """
        Global Monthly Cost Calculator
        ------------------------------
        Get the cost of units used based upon the current ``Pricing`` 
        Tier.

        :units: sms used for the current day that we are expensing
        :units_mtd: mtd sms used excluding the current day
        """
        units_total = units + units_mtd
        units_to_expense = units
        cost = 0

        tiers = self.exclude(end__lte=units_mtd).order_by('start')
        while units_to_expense > 0:
            for t in tiers:
                if units_total >= t.start: # 2500 > 200
                    if units_total >= t.end: # 2500 > 2200
                        # -1 b/c tier2 300-201=99 not 100 for ex
                        units_to_subtract = t.end - (units_mtd if units_mtd >= t.start-1 else t.start-1) # 2200 - 2000
                    else:
                        units_to_subtract = units_to_expense
                    cost += units_to_subtract * t.price
                    units_to_expense -= units_to_subtract
        return cost


class Pricing(AbstractBase):
    """Pricing Tiers that gradually decrease in Price as Volumes increase. 
    Based on monthly volumes."""

    tier = models.PositiveIntegerField(_("Tier"))
    tier_name = models.CharField(_("Tier Name"), max_length=55, blank=True,
        help_text="If blank, will be the Tier's Price per SMS")
    desc = models.CharField(_("Description"), max_length=255, blank=True,
        help_text="Used for Pricing Biz Page Description.")
    price = models.DecimalField(_("Price per SMS"), max_digits=3, decimal_places=2,
        help_text="Price in $'s. Ex: 0.0525")
    start = models.PositiveIntegerField(_("SMS Start"), help_text="Min SMS per Tier")
    end = models.PositiveIntegerField(_("SMS End"), help_text="Max SMS per Tier")

    objects = PricingManager()

    class Meta:
        verbose_name_plural = "Pricing"
        ordering = ('tier',)

    def __str__(self):
        return "Price per SMS: ${:.4f}; SMS range: {}-{}".format(
            self.price, self.start, self.end)

    def save(self, *args, **kwargs):
        """Default ``tier_name`` with the exception of the 'Free Tier'. Middle 
        Tiers use the same ``desc``."""

        if not self.tier_name:
            self.tier_name = "{0:.4f}".format(self.price)

        if not self.desc:
            self.desc = "Next {0:3g}k SMS per month".format((self.end-self.start+1)/1000)

        return super(Pricing, self).save(*args, **kwargs)


##############
# TRANS TYPE #
##############

# Global static list for tests
TRANS_TYPES = [
    ('init_amt', 'init_amt'),
    ('recharge_amt', 'recharge_amt'),
    ('sms_used', 'sms_used'),
    ('phone_number', 'phone_number'),
]

class TransType(AbstractBase):
    """Name and Description for different transaction types.

    Types (to start):
    id  name            desc
    --  --------------  -----------------------
    2   init_amt        initial account funding
    3   recharge_amt    Recharge amount selected by the Hotel
    4   sms_used        daily deduction for sms used for that day; cache - sms used during the day to save DB trips
    5   phone_number    Monthly phone number cost. Is charged at the initial purchase of a phone number, and monthly after that.

    TODO:
        - cache `sms_used` during the day to save DB trips
    """
    name = models.CharField(_("Name"), unique=True, max_length=50)
    desc = models.CharField(_("Description"), max_length=255)

    class Meta:
        verbose_name = "Transaction Type"
        ordering = ['id']

    def __str__(self):
        return self.name


#############
# ACCT COST #
#############

# use a lower charge amount in DEBUG:
if settings.DEBUG:
    INIT_CHARGE_AMT = 100
else:
    INIT_CHARGE_AMT = 500

# AcctCost Amount Choices
CHARGE_AMOUNTS = [(INIT_CHARGE_AMT, '${:.2f}'.format(1))] + [(amt, '${:.2f}'.format(amt/100)) for amt in range(1000, 11000, 1000)]
BALANCE_AMOUNTS = [(100, '${:.2f}'.format(1))] + [(amt, '${:.2f}'.format(amt/100)) for amt in range(1000, 11000, 1000)]


class AcctCostManager(models.Manager):

    def get_or_create(self, hotel, **kwargs):
        '''
        Override `get_or_create` to enforce 1 record p/ Hotel.

        Will - get, create, or update the AcctCost record for the Hotel.
        '''
        try:
            acct_cost = self.get(hotel=hotel)
        except AcctCost.DoesNotExist:
            acct_cost = self.create(hotel=hotel, **kwargs)
            return acct_cost, True
        else:
            for k,v in kwargs.items():
                setattr(acct_cost, k, v)
                acct_cost.save()
            return acct_cost, False


class AcctCost(AbstractBase):
    """
    Initial Charge and Recharge configuration settings here.

    Level: 1 record per Hotel

    Note:

    - All Amounts in Stripe Amount. 
        
        - ex: if DB record = 1000, then amount in dollars = 10.00

    - Will apply discounts as they happen through "Daily AcctTrans" 
    Records.
    """
    hotel = models.OneToOneField(Hotel, related_name='acct_cost')
    init_amt = models.PositiveIntegerField(_("Amount to Add"), 
        choices=CHARGE_AMOUNTS, default=CHARGE_AMOUNTS[0][0])
    balance_min = models.PositiveIntegerField(_("Balance Minimum"),
        choices=BALANCE_AMOUNTS, default=BALANCE_AMOUNTS[0][0])
    recharge_amt = models.PositiveIntegerField(_("Recharge Amount"),
        choices=CHARGE_AMOUNTS, default=CHARGE_AMOUNTS[0][0])
    auto_recharge = models.BooleanField("Auto Recharge On", blank=True, default=True)

    objects = AcctCostManager()

    class Meta:
        verbose_name = "Account Cost"

    def __str__(self):
        return "{} : ${:.2f}".format(self.hotel, self.init_amt/100)


#############
# ACCT STMT #
#############

class AcctStmtManager(Dates, models.Manager):

    def acct_trans_balance(self, hotel, date):
        """
        Calculate the current balance based on sms_used for today.

        Calculate `balance`

        If `balance` < 0, recharge account, and recalculate `balance`

        Return: `balance`
        """
        sms_used = AcctTrans.objects.sms_used_mtd(hotel, insert_date=date)

        balance = AcctTrans.objects.balance(hotel=hotel)

        if balance < hotel.acct_cost.balance_min:
            recharge_amt = AcctTrans.objects.recharge(hotel)
            balance = AcctTrans.objects.balance(hotel=hotel)

        return balance
    
    def get_or_create(self, hotel, month=None, year=None):
        """
        1 Stmt p/Hotel, p/Month, but updated daily until month end.

        Will get, create, or update: single Month's AcctStmt.

        Return: AcctStmt, created
        """
        date = self.first_of_month(month, year)

        total_sms = hotel.messages.monthly_all(date=date).count()
        monthly_costs = (Pricing.objects.get_cost(units=total_sms) +
            hotel.phonenumbers.count() * settings.PHONE_NUMBER_MONTHLY_COST)
        balance = self.acct_trans_balance(hotel, date)

        values = {
            'total_sms': total_sms,
            'monthly_costs': monthly_costs,
            'balance': balance
        }
        try:
            acct_stmt = self.get(hotel=hotel, month=date.month, year=date.year)
            for k,v in values.items():
                setattr(acct_stmt, k, v)
            acct_stmt.save()
            return acct_stmt, False
        except ObjectDoesNotExist:
            acct_stmt = self.create(hotel=hotel, month=date.month, year=date.year,
                **values)
            return acct_stmt, True


class AcctStmt(AbstractBase):
    """
    Monthly usage stats for each hotel.

    :When are AcctStmt's generated?:
        1. Daily
        2. At first login for the day
        3. After a month has ended

    :Level: One record per Hotel per Month.

    :Purpose: Hotels will have a Monthly and Daily view of their Usage.
    """
    # Keys
    hotel = models.ForeignKey(Hotel, related_name='acct_stmt')
    # Auto Fields
    year = models.PositiveIntegerField(_("Year"), blank=True)
    month = models.PositiveIntegerField(_("Month"), blank=True)
    monthly_costs = models.PositiveIntegerField(_("Total Monthly Cost"), blank=True,
        default=settings.DEFAULT_MONTHLY_FEE)
    total_sms = models.PositiveIntegerField(blank=True, default=0)
    balance = models.PositiveIntegerField(_("Current Funds Balance"), blank=True, default=0,
        help_text="Monthly Cost + (SMS Used * Cost Per SMS)")

    objects = AcctStmtManager()

    class Meta:
        ordering = ('-year', '-month',)
        verbose_name = "Account Statement"

    def __str__(self):
        return "{} {}".format(calendar.month_name[self.month], self.year)

    def get_absolute_url(self):
        return reverse('acct_stmt_detail', kwargs={'year':self.year, 'month':self.month})

    @property
    def month_abbr(self):
        return "{} {}".format(calendar.month_abbr[self.month], self.year)


##############
# ACCT TRANS #
##############

class AcctTransQuerySet(models.query.QuerySet):

    def monthly_trans(self, hotel, date):
        """Return all transactions for the Hotel that happened during 
        the month of the supplied date."""
        return (self.filter(hotel=hotel,
                            insert_date__month=date.month,
                            insert_date__year=date.year))

    def balance(self, hotel=None):
        if hotel:
            self = self.filter(hotel=hotel)

        return self.aggregate(Sum('amount'))['amount__sum'] or 0


class AcctTransManager(Dates, models.Manager):

    def get_queryset(self):
        return AcctTransQuerySet(self.model, self._db)

    def monthly_trans(self, hotel, date=None):
        """Default to return the Hotel's current month's transactions 
        if not date is supplied."""
        date = date or self._today
        return self.get_queryset().monthly_trans(hotel, date)

    ### PRE-CREATE ACCT TRANS CHARGE METHODS

    def balance(self, hotel=None):
        '''Sum `amount` for any queryset object.'''
        return self.get_queryset().balance(hotel)

    def recharge(self, hotel):
        """
        If this method is called, either A or B: 

        A. recharge account:
            - charge the c.card
            - create AcctTrans w/ a recharge_amt TransType

        B. raise error that ``recharge`` failed
        """
        balance = self.balance(hotel)
        amount = self.amount_to_recharge(hotel, balance)

        # try:
        #     # charge c.card
        # except:
            # RechargeFailedExcp as e:
            # # TODO: Email Admin, that 'auto_recharge' failed, so 
            # #   the c.card needs to be updated
            # hotel.deactivate()
            # raise e("Recharge account failed.")
        # else:
        # should I set ``trans_type`` as a global VAR b/c doesn't change?

        # TODO: send email, that the c.card was charged

        trans_type, _ = TransType.objects.get_or_create(name='recharge_amt')
        return self.create(
            hotel=hotel,
            trans_type=trans_type,
            amount=amount
        )

    def amount_to_recharge(self, hotel, balance):
        """
        Amount below the ``Hotel.balance_min + Hotel.recharge_amt``
        """
        return (hotel.acct_cost.balance_min - balance) + hotel.acct_cost.recharge_amt

    def check_balance(self, hotel):
        """
        Master Pre-Create AcctTrans method to call that checks 
        `balance`, `auto_recharge`, and `c.card charging` ability 
        before creating the actual AcctTrans.

        :return: None if ok, or raise error.
        """
        balance = self.balance(hotel=hotel)

        if balance > hotel.acct_cost.balance_min:
            return
        else:
            if hotel.acct_cost.auto_recharge:
                self.recharge(hotel)
            else:
                # ``auto_charge`` is OFF and the Account Balance is not 
                # enough to process the transaction.

                # TODO: make Email to send to Admin, to turn 'auto_rechage' ON,
                #   or re-fill account
                hotel.deactivate()
                raise AutoRechargeOffExcp(
                    "Auto-recharge is off, and the account doesn't have "
                    "enough funds to process this transaction."
                )

    ### PHONE_NUMBER

    def phone_number_charge(self, hotel, phone_number):
        """
        Creates an AcctTrans charge for a PH.  This could be an initial 
        charge or monthly.

        :hotel: Hotel object
        :phone_number: twilio ``phone_number`` as a string
        """
        self.check_balance(hotel)
        trans_type, _ = TransType.objects.get_or_create(name='phone_number')
        cost = settings.PHONE_NUMBER_MONTHLY_COST

        return self.create(
            hotel=hotel,
            trans_type=trans_type,
            amount = -cost,
            desc="PH charge {} for PH#: {}".format(cost, phone_number)
        )

    ### SMS_USED

    def sms_used_validate_insert_date(self, insert_date):
        if insert_date >= self._today:
            raise ValidationError(
                "Can only calculate `sms_used` for prior dates. "
                "You submitted: {}".format(insert_date))

    def sms_used_validate_single_date_record(self, hotel, insert_date):
        trans_type = TransType.objects.get(name='sms_used')
        if self.filter(hotel=hotel,
                       insert_date=insert_date,
                       trans_type=trans_type).exists():
            raise ValidationError("Only 1 `sms_used` record per Hotel per Day.")

    def sms_used(self, hotel, insert_date=None):
        '''
        SMS used by a Hotel for a single day. Only call after the 
        day has ended, so it will be the final SMS count, and only 
        calculated once.
        '''
        # pre-validation
        self.sms_used_validate_insert_date(insert_date)
        self.sms_used_validate_single_date_record(hotel, insert_date)

        # static `trans_type`
        trans_type = TransType.objects.get(name='sms_used')
        
        # SMS counts needed to get the daily incremental "sms_used" cost
        sms_used = hotel.messages.filter(insert_date=insert_date).count()
        sms_used_mtd = self.sms_used_mtd(hotel, insert_date)
        
        return self.create(
            hotel=hotel,
            trans_type=trans_type,
            amount= -Pricing.objects.get_cost(units=sms_used, units_mtd=sms_used_mtd),
            sms_used=sms_used,
            insert_date=insert_date
        )

    def sms_used_mtd(self, hotel, insert_date):
        """
        MTD SMS used by the Hotel.

        If the Hotel hasn't sent any SMS, this will return "None", so 
        always return "0" instead.
        """
        trans_type = TransType.objects.get(name="sms_used")
        sms_used_mtd = (self.filter(trans_type=trans_type)
                            .monthly_trans(hotel=hotel, date=insert_date)
                            .aggregate(Max('sms_used'))['sms_used__max'])
        return sms_used_mtd or 0

    ### GET_OR_CREATE

    def get_or_create(self, hotel, trans_type, date=None):
        """
        Use get_or_create, so as not to duplicate charges, or daily records

        `sms_used` - get's the SMS used for the day, and calculates the cost.
        `init_amt` - initial funding amount
        `recharge_amt` - recharge funding amount
        """
        date = date or self._today

        if trans_type.name == 'sms_used':
            sms_used = hotel.messages.filter(insert_date=date).count()
            acct_tran = self.sms_used(hotel, date)
            # check if balance < 0, if so charge C.Card, and if fail, suspend Twilio Acct.
            # don't worry about raising an error here.  Twilio Acct will be suspended
            # and an email will be sent to myself and the Hotel of the C.Card Charge fail.
            recharge = self.check_balance(hotel)
            return acct_tran, True

        elif trans_type.name in ('init_amt', 'recharge_amt'):
            amount = getattr(hotel.acct_cost, trans_type.name)
            acct_tran = self.create(
                hotel=hotel,
                trans_type=trans_type,
                insert_date=date,
                amount=amount
            )
            return acct_tran, True
        

class AcctTrans(AbstractBase):
    """
    Account Transactions per: Hotel / TransType / Day.

    :insert_date: `datetime` b/c some `trans_types` could happen more than 1x p/ day
    :sms_used: 1 transaction p/ day for total sms used

    :Goal:
        To keep a running balance by day of how much the Hotel 
        is using, and also to be able to provide "Alerts" for low account 
        balances.
    """
    # Keys
    hotel = models.ForeignKey(Hotel, related_name='acct_trans')
    trans_type = models.ForeignKey(TransType)
    # Auto
    amount = models.IntegerField(_("Amount"), blank=True, null=True,
        help_text="Negative for Usage, Positive for 'Funds Added' records.")
    desc = models.CharField(max_length=100, blank=True, null=True,
        help_text="Use to store additional filter logic")
    sms_used = models.PositiveIntegerField(blank=True, null=True,
        help_text="NULL unless trans_type=sms_used")
    insert_date = models.DateField(_("Insert Date"), blank=True, null=True) # remove in Prod (use ``created``)
    balance = models.PositiveIntegerField(_("Balance"), blank=True, null=True,
        help_text="Current blance, just like in a Bank Account.")

    objects = AcctTransManager()

    class Meta:
        verbose_name = "Account Transaction"
        ordering = ('-insert_date',)

    def __str__(self):
        return "Date: {self.insert_date} Hotel: {self.hotel} TransType: {self.trans_type} \
Amount: ${amount:.2f}".format(self=self, amount=self.amount/100.0)

    def save(self, *args, **kwargs):
        # For testing only
        if not self.insert_date:
            self.insert_date = timezone.now().date()

        if not self.balance:
            current_balance = AcctTrans.objects.balance(hotel=self.hotel)
            amount = self.amount or 0
            self.balance = current_balance + amount

        return super(AcctTrans, self).save(*args, **kwargs)