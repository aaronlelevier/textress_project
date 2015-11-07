from __future__ import absolute_import

from celery import shared_task

from account.models import AcctTrans, TransType, AcctStmt
from main.models import Hotel



@shared_task
def create_initial_acct_trans_and_stmt(hotel_id):
    hotel = Hotel.objects.get(id=hotel_id)
    init_amt_type = TransType.objects.get(name='init_amt')

    acct_tran, _ = AcctTrans.objects.get_or_create(hotel=hotel,
        trans_type=init_amt_type)

    acct_stmt, _ = AcctStmt.objects.get_or_create(hotel=hotel)
