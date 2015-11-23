from __future__ import absolute_import

import sys
import calendar
import datetime
import pytz

from django.db import models
from django.db.models import Max, Sum, Q
from django.conf import settings
from django.core.cache import cache
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
from payment.models import Charge
from utils import email
from utils.exceptions import RechargeFailedExcp, AutoRechargeOffExcp
from utils.models import Dates, TimeStampBaseModel


###########
# PRICING #
###########

class Pricing(TimeStampBaseModel):
    """
    Pricing per SMS will be fixed, and will be $0.05 per SMS unless there is a business
    need to do otherwise.
    """
    hotel = models.OneToOneField(Hotel, related_name='pricing', blank=True, null=True)
    cost = models.FloatField(blank=True, default=settings.DEFAULT_SMS_COST,
        help_text="Price in Stripe units, so -> 5.00 == $0.05")

    class Meta:
        verbose_name_plural = "Pricing"

    def __str__(self):
        return "Hotel: {}; Price per SMS: ${:.2f}".format(self.hotel, self.cost)

    def save(self, *args, **kwargs):
        if not self.hotel:
            self.check_for_default_pricing()
        return super(Pricing, self).save(*args, **kwargs)

    def check_for_default_pricing(self):
        """
        Only allow one Pricing Obj to have a blank Hotel FK
        to be used w/ 'index.html'
        """
        default = Pricing.objects.filter(hotel__isnull=True)

        if self.id:
            default = default.exclude(id=self.id)

        if default:
            raise Exception("Default Pricing object with No Hotel already exists.")

    def get_cost(self, sms_used_count):
        """
        ** Always Negative **
        Expenses are negative, added Funds are Positive.
        """
        return -(self.cost * sms_used_count)


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

class TransType(TimeStampBaseModel):
    """Name and Description for different transaction types.

    Types (to start):
    id  name            desc
    --  --------------  -----------------------
    2   init_amt        initial account funding
    3   recharge_amt    Recharge amount selected by the Hotel
    4   sms_used        daily deduction for sms used for that day; cache - sms used during the day to save DB trips
    5   phone_number    Monthly phone number cost. Is charged at the initial purchase of a phone number, and monthly after that.
    """
    name = models.CharField(_("Name"), unique=True, max_length=50)
    desc = models.CharField(_("Description"), max_length=255)

    class Meta:
        verbose_name = "Transaction Type"

    def __str__(self):
        return self.name


class TransTypeCache(object):

    def __init__(self):
        self.trans_types = [x[0] for x in TRANS_TYPES]

        for t in self.trans_types:
            setattr(self, t, self.get_or_set_value(t))

    def get_or_set_value(self, name):
        value = cache.get(name)
        if not value:
            cache.set(name, TransType.objects.get(name=name))
        return cache.get(name)


#############
# ACCT COST #
#############

# AcctCost Amount Choices
INIT_CHARGE_AMOUNT = 500
CHARGE_AMOUNTS = [(INIT_CHARGE_AMOUNT, '${:.2f}'.format(INIT_CHARGE_AMOUNT/100))] + \
    [(amt, '${:.2f}'.format(amt/100)) for amt in range(1000, 11000, 1000)]

INIT_BALANCE_AMOUNT = 100
BALANCE_AMOUNTS = [(INIT_BALANCE_AMOUNT, '${:.2f}'.format(INIT_BALANCE_AMOUNT/100))] + \
    [(amt, '${:.2f}'.format(amt/100)) for amt in range(1000, 11000, 1000)]


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


class AcctCost(TimeStampBaseModel):
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
        choices=CHARGE_AMOUNTS, default=CHARGE_AMOUNTS[0][0],
        help_text="A higher Recharge Amount is recommended to decrease payment transactions.")
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

    def starting_balance(self, hotel, date=None):
        date = date or self._today
        prev_month = self.prev_month(date)
        prev_year = self.prev_year(date)

        try:
            return self.get(hotel=hotel, month=prev_month, year=prev_year).balance
        except AcctStmt.DoesNotExist:
            return 0
    
    def get_or_create(self, hotel, month=None, year=None):
        """
        1 Stmt p/Hotel, p/Month, but updated daily until month end.

        Will get, create, or update: single Month's AcctStmt.

        Return: AcctStmt, created
        """
        date = self.first_of_month(month, year)

        # sms fields: re-calculate 'sms_used' for today in order to get most
        # up to date usage balance
        AcctTrans.objects.update_or_create_sms_used(hotel, self._today) 
        total_sms = hotel.messages.monthly_all(date=date).count()
        total_sms_costs = self.get_total_sms_costs(hotel, total_sms)
        # other fields
        funds_added = AcctTrans.objects.funds_added(hotel, date)
        phone_numbers = hotel.phone_numbers.count()
        monthly_costs = self.get_monthly_costs(hotel, date)
        balance = AcctTrans.objects.monthly_trans(hotel, date).balance()

        values = {
            'funds_added': funds_added,
            'phone_numbers': phone_numbers,
            'total_sms': total_sms,
            'total_sms_costs': total_sms_costs,
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

    @staticmethod
    def get_total_sms_costs(hotel, total_sms):
        try:
            return hotel.pricing.get_cost(total_sms)
        except Exception: # RelatedObjectDoesNotExist
            return -(total_sms * settings.DEFAULT_SMS_COST)

    @staticmethod
    def get_monthly_costs(hotel, date):
        """
        'phone_number' is the only current ``trans_type`` w/ a monthly cost.
        """
        return (AcctTrans.objects.monthly_trans(hotel, date)
                                 .filter(trans_type__name='phone_number')
                                 .balance())


class AcctStmt(TimeStampBaseModel):
    """
    Monthly usage stats for each hotel.

    :When are AcctStmt's generated?:
        1. Daily (3 am) <- planned time
        3. After a month has ended (Final month-end Stmt)

    :Level: One record per Hotel per Month.

    :Purpose: Hotels will have a Monthly and Daily view of their Usage.
    """
    # Keys
    hotel = models.ForeignKey(Hotel, related_name='acct_stmt')
    # Auto Fields
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    funds_added = models.PositiveIntegerField(blank=True, default=0,
        help_text="from 'init_amt' or 'recharge_amt' AcctTrans.")
    phone_numbers = models.PositiveIntegerField(blank=True, default=0)
    monthly_costs = models.IntegerField(blank=True, default=0,
        help_text="Only active Phone Numbers have a monthly cost at this time, \
but other costs may be added. Additional feature costs, surcharge for REST API access, etc...")
    total_sms = models.PositiveIntegerField(blank=True, default=0)
    total_sms_costs = models.IntegerField(blank=True, default=0,
        help_text="This will be negative (debits are negative).")
    balance = models.IntegerField(_("Current Funds Balance"), blank=True, default=0)

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
        """
        Return all transactions for the ``hotel`` that happened during 
        the month of the given ``date``.
        """
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

    def balance(self, hotel=None):
        '''
        Calculates current balance (Expensive).
        '''
        return self.get_queryset().balance(hotel)

    @property
    def trans_types(self):
        return TransTypeCache()

    def check_balance(self, hotel):
        """
        Daily, or more often if high SMS volumes, check the Funds ``balance``
        of the Hotel to see if a ``recharge`` is required.

        Before this method: run ``update_or_create_sms_used`` so that all charges
        are posted.
        """
        self.update_or_create_sms_used(hotel)
        balance = self.get_balance(hotel)
        recharge_required = self.check_recharge_required(hotel, balance)

        if recharge_required:
            recharge_amt = self.calculate_recharge_amount(hotel, balance)
            self.recharge(hotel, recharge_amt)

    def recharge(self, hotel, recharge_amt):
        if not hotel.acct_cost.auto_recharge:
            self.handle_auto_recharge_failed(hotel)

        # if ``charge_hotel`` is called here, all ``recharge`` tests will need a Stripe
        # Customer in order to pass, and will run slow b/c have to hit the Stripe API ea time.
        if 'test' not in sys.argv:
            self.charge_hotel(hotel, recharge_amt)

        return self.create(
            hotel=hotel,
            trans_type=self.trans_types.recharge_amt,
            amount=recharge_amt
        )

    @staticmethod
    def handle_auto_recharge_failed(hotel):
        email.send_auto_recharge_failed_email(hotel)
        hotel.deactivate()
        raise AutoRechargeOffExcp(
            "Auto-recharge is off, and the account doesn't have "
            "enough funds to process this transaction."
        )

    @staticmethod
    def charge_hotel(hotel, amount):
        try:
            charge = Charge.objects.stripe_create(hotel, amount)
        except stripe.error.StripeError:
              email.send_charge_failed_email(hotel, amount)
              hotel.deactivate()
              raise
        else:
            hotel.activate()
            email.send_account_charged_email(hotel, charge)

    def update_or_create_sms_used(self, hotel, date=None):
        """
        Complete regardless of there being "zero" SMS for the date.
        """
        date = date or self._today

        try:
            acct_trans = self.get(hotel=hotel, trans_type=self.trans_types.sms_used,
                insert_date=date)
        except AcctTrans.DoesNotExist:
            return self.create_sms_used(hotel, date)
        else:
            sms_used_count = self.sms_used_count(hotel, date)
            if acct_trans.sms_used == sms_used_count:
                return acct_trans
            else:
                return self.update_hotel_sms_used(acct_trans, hotel, sms_used_count)

    # @staticmethod
    def update_hotel_sms_used(self, acct_trans, hotel, sms_used_count):
        """
        ``pricing.get_cost`` will always return a negative (debits are negative)
        so as we add "sms cost", "amount" goes down.
        """
        sms_used_cost = hotel.pricing.get_cost(sms_used_count)

        acct_trans.sms_used = sms_used_count
        acct_trans.amount = sms_used_cost
        acct_trans.balance = self.get_balance(hotel, excludes=True) + sms_used_cost
        acct_trans.save()

        return acct_trans

    def sms_used_count(self, hotel, date=None):
        date = date or self._today
        return hotel.messages.filter(insert_date=date).count()

    def create_sms_used(self, hotel, date):
        # SMS counts needed to get the daily incremental "sms_used" cost
        sms_used = self.sms_used_count(hotel, date)
        sms_used_prior_mtd = self.sms_used_mtd_prior_to_this_date(hotel, date)
        amount = hotel.pricing.get_cost(sms_used)

        return self.create(
            hotel=hotel,
            trans_type=self.trans_types.sms_used,
            amount=amount,
            sms_used=sms_used,
            insert_date=date
        )

    def sms_used_mtd_prior_to_this_date(self, hotel, date=None):
        """
        Calculate MTD sms_used prior to ``date``. Main purpose is to calculate
        the "sms used as of yesterday" but can be used for any date.
        """
        date = date or self._today
        date_prior = date - datetime.timedelta(days=1)

        if date_prior.month != date.month:
            return 0

        return (AcctTrans.objects.filter(hotel=hotel,
                                         insert_date__month=date.month,
                                         insert_date__lte=date)
                                  .aggregate(Sum('sms_used'))['sms_used__sum']) or 0

    def get_balance(self, hotel, excludes=None):
        """
        Cheaply get the Hotel's Funds 'balance' without Summing all
        acct_trans record amounts.
        """
        qs = self.filter(hotel=hotel)

        if excludes:
            qs = qs.exclude(
                Q(trans_type=self.trans_types.sms_used) & \
                Q(insert_date=self._today)    
            )

        last_acct_trans = qs.order_by('modified').last()

        return self.resolve_last_trans_balance(last_acct_trans)

    @staticmethod
    def resolve_last_trans_balance(last_acct_trans):
        try:
            if not last_acct_trans.balance:
                balance = 0
            else:
                balance = last_acct_trans.balance
        except AttributeError:
            balance = 0

        return balance

    @staticmethod
    def check_recharge_required(hotel, balance):
        return balance < hotel.acct_cost.balance_min

    @staticmethod
    def calculate_recharge_amount(hotel, balance):
        return hotel.acct_cost.recharge_amt - balance

    def phone_number_charge(self, hotel, phone_number, desc=None):
        """
        Creates an AcctTrans charge for a PH.  This could be an initial 
        charge or monthly.

        :hotel: Hotel object
        :phone_number: twilio ``phone_number`` as a string
        :desc:
            to be used to differentiate from "monthly phone_number charges 
            vs. first time purchase charge.
        """
        self.check_balance(hotel)
        amount = -(settings.PHONE_NUMBER_MONTHLY_COST)

        if 'test' not in sys.argv:
            self.charge_hotel(hotel, amount)

        return self.create(
            hotel=hotel,
            trans_type=self.trans_types.phone_number,
            amount=amount,
            desc=desc or "PH charge ${:.2f} for PH#: {}".format(amount/100, phone_number)
        )

    def sms_used_mtd(self, hotel, insert_date):
        """
        MTD SMS used by the Hotel.

        NOTE: Used by ``AcctStmt``
        """
        trans_type = self.trans_types.sms_used

        sms_used_mtd = (self.filter(trans_type=trans_type)
                            .monthly_trans(hotel=hotel, date=insert_date)
                            .aggregate(Max('sms_used'))['sms_used__max'])
        return sms_used_mtd or 0

    ### LEGACY METHODS THAT ARE STILL "NEED TO BE REFACTORED WIP" ###

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
            acct_tran = self.update_or_create_sms_used(hotel, date)
            return acct_tran, True

        elif trans_type.name == 'init_amt':
            return self.get_or_create_init_amt(hotel, date)

        elif trans_type.name == 'recharge_amt':
            return self.get_or_create_recharge_amt(hotel, date)

    def get_or_create_init_amt(self, hotel, date):
        amount = hotel.acct_cost.init_amt
        trans_type = self.trans_types.init_amt

        acct_tran = self.create(
            hotel=hotel,
            trans_type=trans_type,
            insert_date=date,
            amount=amount,
            balance=amount
        )
        return acct_tran, True

    def get_or_create_recharge_amt(self, hotel, date):
        amount = hotel.acct_cost.recharge_amt
        trans_type = self.trans_types.recharge_amt

        acct_tran = self.create(
            hotel=hotel,
            trans_type=trans_type,
            insert_date=date,
            amount=amount
        )
        return acct_tran, True

    def funds_added(self, hotel, date=None):
        return (self.monthly_trans(hotel, date)
                    .filter(trans_type__name__in=['init_amt', 'recharge_amt'])
                    .aggregate(Sum('amount'))['amount__sum'] or 0)


class AcctTrans(TimeStampBaseModel):
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
    sms_used = models.PositiveIntegerField(blank=True, default=0,
        help_text="NULL unless trans_type=sms_used")
    insert_date = models.DateField(_("Insert Date"), blank=True, null=True)
    balance = models.PositiveIntegerField(_("Balance"), blank=True,
        help_text="Current blance, just like in a Bank Account.")

    objects = AcctTransManager()

    class Meta:
        verbose_name = "Account Transaction"
        ordering = ('-insert_date',)

    def __str__(self):
        return "Date: {self.insert_date} Hotel: {self.hotel} TransType: {self.trans_type} \
Amount: ${amount:.2f}".format(self=self, amount=float(self.amount)/100.0)

    def save(self, *args, **kwargs):
        # For testing only
        if not self.insert_date:
            self.insert_date = timezone.now().date()

        self.update_balance()

        return super(AcctTrans, self).save(*args, **kwargs)

    def update_balance(self):
        if self.trans_type.name == 'sms_used':
            self.balance = AcctTrans.objects.get_balance(
                hotel=self.hotel, excludes=True) + self.amount
        else:
            self.balance = AcctTrans.objects.get_balance(hotel=self.hotel) + self.amount
