import calendar
import datetime

from django.db import models
from django.db.models import Max, Sum
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from main.models import Hotel


class Dates(object):

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


class AbstractBase(Dates, models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


###########
# PRICING #
###########

class PricingManager(models.Manager):

    def get_cost(self, units, units_prev=0):
        """
        Global Monthly Cost Calculator
        ------------------------------
        Get the cost of units used based upon the current ``Pricing`` 
        Tier.

        units - current units used this month
        units_prev - previous units balance calculated for this month
        """
        tiers = self.order_by('-end')
        units_to_expense = units - units_prev
        cost = 0
        while units_to_expense > 0:
            for t in tiers:
                if units >= t.start:
                    if units >= t.end:
                        # -1 b/c tier2 300-201=99 not 100 for ex
                        units_to_subtract = t.end - (t.start if t.start == 0 else t.start-1)
                    else:
                        units_to_subtract = units - (t.start if t.start == 0 else t.start-1)
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
    price = models.DecimalField(_("Price per SMS"), max_digits=5, decimal_places=4,
        help_text="Price in $'s. Ex: 0.0525")
    start = models.PositiveIntegerField(_("SMS Start"), help_text="Min SMS per Tier")
    end = models.PositiveIntegerField(_("SMS End"), help_text="Max SMS per Tier")

    objects = PricingManager()

    class Meta:
        verbose_name_plural = "Pricing"
        ordering = ('tier',)

    def __str__(self):
        return "{0:.4f}".format(self.price)

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
    ('bulk_discount', 'bulk_discount')
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
    6   bulk_discount   credit applied from previous months use based on bulk

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
            acct_cost = AcctCost.objects.get(hotel=hotel)
        except ObjectDoesNotExist:
            acct_cost = AcctCost.objects.create(hotel=hotel, **kwargs)
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

    - Used to have a ``per_sms`` static cost here, and I was going to 
    adjust billing at the end of the month for the ``bulk_discount``.  
    
    - NOW: will apply discounts as they happen through "Daily AcctTrans" 
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

class AcctStmtManager(models.Manager):

    def acct_trans_balance(self, hotel, date):
        """
        Calculate the current balance based on sms_used for today.

        Calculate `balance`

        If `balance` < 0, recharge account, and recalculate `balance`

        Return: `balance`
        """
        sms_used, created = AcctTrans.objects.sms_used(hotel, insert_date=date)

        balance = AcctTrans.objects.filter(hotel=hotel).balance()

        if balance < hotel.acct_cost.balance_min:
            recharge_amt = AcctTrans.objects.recharge(hotel, balance)
            balance = AcctTrans.objects.filter(hotel=hotel).balance()

        return balance
    
    def get_or_create(self, hotel, month=timezone.now().month, year=timezone.now().year):
        """
        1 Stmt p/Hotel, p/Month, but updated daily upon User request.

        Will get, create, or update - current month record.

        Return: AcctStmt, created
        """
        date = datetime.date(year, month, 1)
        total_sms = hotel.messages.monthly_all(date=date).count()

        values = {
            'total_sms': total_sms,
            'monthly_costs': 3, #Pricing.objects.get_cost(units=total_sms),
            'balance': self.acct_trans_balance(hotel, date)
        }
        try:
            acct_stmt = self.get(hotel=hotel, month=month, year=year)
            for k,v in values.items():
                setattr(acct_stmt, k, v)
            acct_stmt.save()
            return acct_stmt, False
        except ObjectDoesNotExist:
            acct_stmt = self.create(hotel=hotel, month=month, year=year,
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

    def monthly_trans(self, hotel, month, year):
        return (self.filter(hotel=hotel,
                            insert_date__month=month,
                            insert_date__year=year))

    def previous_monthly_trans(self, hotel, month, year):
        first_of_month = datetime.date(int(year), int(month), 1)
        return self.filter(hotel=hotel, insert_date__lt=first_of_month)

    def balance(self):
        return self.aggregate(Sum('amount'))['amount__sum'] or 0


class AcctTransManager(Dates, models.Manager):

    def get_queryset(self):
        return AcctTransQuerySet(self.model, self._db)

    def monthly_trans(self, hotel, month=timezone.now().month, year=timezone.now().year):
        return self.get_queryset().monthly_trans(hotel=hotel,
            month=month, year=year)

    def previous_monthly_trans(self, hotel, month, year):
        '''All transactions b/4 the `month` and `year`.'''
        return self.get_queryset().previous_monthly_trans(hotel=hotel,
            month=month, year=year)

    def balance(self):
        '''Sum `amount` for any queryset object.'''
        return self.get_queryset().balance()

    def sms_used_max_date(self):
        sms_used = TransType.objects.get(name='sms_used')
        return (self.filter(trans_type=sms_used)
                    .aggregate(Max('insert_date'))['insert_date__max'])

    def sms_used_on_date(self, date):
        return self.sms_used_max_date() == date

    def amount(self, hotel, trans_type):
        '''Return the Amount ($) based on the Hotel,TransType.'''
        acct_cost = AcctCost.objects.get(hotel=hotel)
        return getattr(acct_cost, trans_type.name)

    def phone_number_charge(self, hotel, desc):
        """
        Creates an AcctTrans charge for a PH.  This could be an initial 
        charge or monthly.

        :hotel: Hotel object
        :desc: twilio ``phone_number`` as a string
        """
        self.check_balance(hotel)
        trans_type, _ = TransType.objects.get_or_create(name='phone_number',
            desc='phone_number')
        acct_tran = self.create(hotel=hotel, trans_type=trans_type,
            amount= -settings.PHONE_NUMBER_MONTHLY_COST, desc=desc)
        return acct_tran

    def recharge(self, hotel, balance):
        '''
        Should only occur if the ``balance`` is less than the ``balance_min`` 
        for the Hotel.

        :ex: 
            acct_cost.balance_min = 1000
            current balance = -25
            recharge_amt - current balance = 1000-(-25) = 1025

        :Return:
            acct_tran, created
        '''
        balance_ok = balance > hotel.acct_cost.balance_min

        if balance_ok:
            return None, False
        else:
            amount = hotel.acct_cost.balance_min - balance

            # TODO: need to charge credit card here in order to "recharge"
            #   the account

            # should I set ``trans_type`` as a global VAR b/c doesn't change?
            trans_type = get_object_or_404(TransType, name='recharge_amt')
            acct_tran = self.create(hotel=hotel, trans_type=trans_type, amount=amount)
            return acct_tran, True

    def check_balance(self, hotel):
        '''
        Returns a Boolean if the Account balance is more than the 
        ``hotel.acct_cost.balance_min``

        :hotel: Hotel object
        '''
        balance = AcctTrans.objects.filter(hotel=hotel).balance()

        if balance > hotel.acct_cost.balance_min:
            return True
        else:
            if hotel.acct_cost.auto_recharge:
                acct_tran, charged = self.recharge(hotel, balance)
                return True
            else:
                # ``auto_charge`` is OFF and the Account Balance is not 
                # enought to process the transaction.
                return False

    def sms_used(self, hotel, trans_type=None, insert_date=None):
        '''
        get_or_create() the `sms_used` record p/Hotel p/Day.

        Return: acct_tran, created
        '''
        trans_type = TransType.objects.get(name='sms_used')
        
        # get all hotel messages for the month based on "sent"
        sms_used = hotel.messages.monthly_all(insert_date).count()
        # vs. what has been accounted for
        sms_used_prev = self.sms_used_prev(hotel)
        
        values = {
            'sms_used': sms_used,
            'amount': Pricing.objects.get_cost(units=sms_used, units_prev=sms_used_prev)
        }
        if not sms_used:
            return None, None
        else:
            try:
                acct_tran = self.get(hotel=hotel, trans_type=trans_type, insert_date=insert_date)
                for k,v in values.items():
                    setattr(acct_tran, k, v)
                return acct_tran.save(), False
            except ObjectDoesNotExist:
                acct_tran = self.create(hotel=hotel, trans_type=trans_type, insert_date=insert_date,
                    **values)
                return acct_tran, True

    def sms_used_prev(self, hotel):
        """
        MTD SMS used by the Hotel.

        If the Hotel hasn't sent any SMS, this will return "None", so 
        always return "0" instead.
        """
        sms_used_prev = (self.monthly_trans(hotel=hotel)
                             .aggregate(Max('sms_used'))['sms_used__max'])
        return sms_used_prev or 0

    def get_or_create(self, hotel, trans_type, *args, **kwargs):
        """
        Use get_or_create, so as not to duplicate charges, or daily records

        `init_amt` - initial funding amount
        `recharge_amt` - recharge funding amount
        `sms_used` - get's the SMS used for the day, and calculates the cost.
        `bulk_discount` - amount is not predefined for this b/c will vary
            based on usage.

        """
        insert_date = kwargs.get('insert_date', self._today)
        
        if trans_type.name == 'sms_used':
            sms_used = hotel.messages.filter(insert_date=insert_date).count()
            acct_tran, created = self.sms_used(hotel, trans_type, insert_date)

            # check if balance < 0, if so charge C.Card, and if fail, suspend Twilio Acct.
            # don't worry about raising an error here.  Twilio Acct will be suspended
            # and an email will be sent to myself and the Hotel of the C.Card Charge fail.
            recharge = self.check_balance(hotel)

        elif trans_type.name in ('init_amt', 'recharge_amt'):
            amount = self.amount(hotel, trans_type)
            acct_tran = self.create(hotel=hotel, trans_type=trans_type,
                insert_date=insert_date, amount=amount)
            created = True

        return acct_tran, created
        

class AcctTrans(AbstractBase):
    """
    Account Transactions per day.

    :sms_used:
        1 transaction p/ day for total sms used

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
        return super(AcctTrans, self).save(*args, **kwargs)


@receiver(post_save, sender=AcctTrans)
def update_balance(sender, instance=None, created=False, **kwargs):
    '''Update the current ``balance`` on the Account after the last 
    transaction has been saved.

    Don't check the ``balance`` on the day of signup b/c will cause 
    an infinte loop b/c nothing to check yet.

    :TODO: Drop this off to a Celery Task so doesn't cause an infinite loop.
    '''
    if not instance.balance and (instance.created.date != instance.modified.date):
        instance.balance = AcctTrans.objects.balance()
        instance.save()
