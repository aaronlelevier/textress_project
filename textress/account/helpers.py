from account.models import AcctTrans, TransType


def get_or_create_sms_used(hotel, date=None):
    trans_type, _ = TransType.objects.get_or_create(name='sms_used')
    return AcctTrans.objects.get_or_create(hotel, trans_type, date)
