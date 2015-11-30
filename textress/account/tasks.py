"""
Future Periodic Tasks
---------------------
that will need to be scheduled

:cron SO answer: http://stackoverflow.com/a/11775112/1913888

Tasks
-----
1. Check daily for all registered PHs, if 30 days since the last 
PH charge date, then charge.

:cron:
    * /12 * * * /path/to/script/to/run.py   # runs every 12 hours

:logic:
    if today.date - last_ph_num_charge.date > 30:
        charge for ph num

"""
from __future__ import absolute_import

from django.conf import settings

from celery import shared_task

from account.models import AcctTrans, TransType, AcctStmt, Pricing
from main.models import Hotel
from utils.models import Dates


@shared_task
def create_initial_acct_trans_and_stmt(hotel_id):
    """
    Run after 'registration payment', so when Admin goes to 
    'Billing Summary' page it isn't blank, and shows initial funds.
    """
    hotel = Hotel.objects.get(id=hotel_id)

    Pricing.objects.get_or_create(hotel=hotel)

    init_amt_type = TransType.objects.get(name='init_amt')

    AcctTrans.objects.get_or_create(hotel=hotel,
        trans_type=init_amt_type)

    AcctStmt.objects.get_or_create(hotel=hotel)


@shared_task
def get_or_create_acct_stmt(hotel_id, month, year):
    """
    To be run daily for each Hotel to update their 'AcctStmt'
    """
    hotel = Hotel.objects.get(id=hotel_id)
    return AcctStmt.objects.get_or_create(hotel, month, year)


@shared_task
def get_or_create_acct_stmt_all_hotels(month, year):
    """
    Master scheduled 'AcctStmt' task to update all Hotels.
    """
    for hotel in Hotel.objects.all():
        get_or_create_acct_stmt.delay(hotel.id, month, year)


@shared_task
def charge_hotel_monthly_for_phone_numbers(hotel_id):
    """
    Creates a single monthly charge per active 'Phone Number' 
    based upon the 'CHARGE_DAY' set in the 'settings'.
    """
    dates = Dates()
    today = dates._today.day

    if today == settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY:
        hotel = Hotel.objects.get(id=hotel_id)
        
        for ph in hotel.phone_numbers.all():
            try:
                AcctTrans.objects.get(
                    hotel=hotel,
                    trans_type__name='phone_number',
                    insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY,
                    desc=ph.monthly_charge_desc
                )
            except AcctTrans.DoesNotExist:
                AcctTrans.objects.phone_number_charge(
                    hotel=hotel, 
                    phone_number=ph.phone_number,
                    desc=ph.monthly_charge_desc
                )


@shared_task
def charge_hotel_monthly_for_phone_numbers_all_hotels():
    for hotel in Hotel.objects.all():
        charge_hotel_monthly_for_phone_numbers.delay(hotel.id)


@shared_task
def eod_update_or_create_sms_used():
    """
    After a day has passed, run the final ``update_or_create_sms_used`` 
    to get the final 'sms' counts/costs for that day for all active Hotels.
    """
    dates = Dates()
    yesterday = dates._yesterday

    for hotel in Hotel.objects.current():
        AcctTrans.objects.update_or_create_sms_used(hotel, yesterday)
