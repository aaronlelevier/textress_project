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

from datetime import date, timedelta

from celery import shared_task

from django.utils import timezone

from account.models import AcctTrans, TransType, AcctStmt
from main.models import Hotel


@shared_task
def monthly_ph_charge():
    '''
    Charge any PH where it has been 30 days since the last 
    charge, for all Hotels.
    '''
    # setup
    trans_type = TransType.objects.get('phone_number')
    today = timezone.now().date()

    for hotel in Hotel.objects.all():
        for phone in hotel.phonenumbers.all():
            last_charge = AcctTrans.objects.filter(hotel=hotel,
                desc=phone.phone_number).order_by('-created').last()
            # if not last_charge:
                # TODO: LOG HERE
            
            if today - last_charge.date > timedelta(days=30):
                AcctTrans.objects.phone_number_charge(hotel,
                    phone_number=phone.phone_number)

@shared_task
def create_initial_acct_trans_and_stmt(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    init_amt_type = TransType.objects.get(name='init_amt')

    acct_tran, _ = AcctTrans.objects.get_or_create(hotel=hotel,
        trans_type=init_amt_type)

    acct_stmt, _ = AcctStmt.objects.get_or_create(hotel=hotel)
