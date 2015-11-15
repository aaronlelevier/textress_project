from __future__ import absolute_import

from celery import shared_task

from account.models import AcctTrans, TransType, AcctStmt, Pricing
from main.models import Hotel


@shared_task
def create_initial_acct_trans_and_stmt(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)

    Pricing.objects.get_or_create(hotel=hotel)

    init_amt_type = TransType.objects.get(name='init_amt')

    AcctTrans.objects.get_or_create(hotel=hotel,
        trans_type=init_amt_type)

    AcctStmt.objects.get_or_create(hotel=hotel)
