from __future__ import absolute_import

from django.conf import settings

from celery import shared_task

from account.models import AcctTrans, TransType, AcctStmt, Pricing
from main.models import Hotel
from utils.models import Dates


@shared_task
def create_initial_acct_trans_and_stmt(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)

    Pricing.objects.get_or_create(hotel=hotel)

    init_amt_type = TransType.objects.get(name='init_amt')

    AcctTrans.objects.get_or_create(hotel=hotel,
        trans_type=init_amt_type)

    AcctStmt.objects.get_or_create(hotel=hotel)


@shared_task
def get_or_create_acct_stmt(hotel_id, month, year):
    hotel = Hotel.objects.get(id=hotel_id)
    return AcctStmt.objects.get_or_create(hotel, month, year)


@shared_task
def charge_hotel_monthly_for_phone_numbers(hotel_id):
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
def eod_update_or_create_sms_used():
    """
    After a day has passed, run the final ``update_or_create_sms_used`` 
    to get the final 'sms' counts/costs for that day for all active Hotels.
    """
    dates = Dates()
    yesterday = dates._yesterday

    for hotel in Hotel.objects.current():
        AcctTrans.objects.update_or_create_sms_used(hotel, yesterday)
