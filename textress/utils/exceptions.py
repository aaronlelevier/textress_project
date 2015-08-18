from django.core.exceptions import ValidationError

from rest_framework.exceptions import APIException


### REST ###

class NotHotelGuestException(APIException):
    status_code = 400
    default_detail = 'Not a valid Hotel Guest.'


class HotelGuestNotFoundException(APIException):
    status_code = 400
    default_detail = 'Hotel Guest Not Found.'


### Account ###

class RechargeAccountRequiredExcp(Exception):

    def __init__(self, *args, **kwargs):
        super(RechargeAccountRequiredExcp, self).__init__(
            "Unable to process transaction. Please recharge the account balance.")


### Concierge ###

class ReplyNotFound(Exception):
    pass


### Main ###

class HotelPhoneNotFound(Exception):
    pass


### SMS Business Site Test Send ###

class DailyLimit(Exception):

    def __init__(self, *args, **kwargs):
        super(DailyLimit, self).__init__("Daily text message limit reached")


class PhoneNumberNotDeletedExcp(Exception):
    pass


# TODO: maybe add cost args to this, so show in error msg
class ConvertCostException(Exception):
    pass

class CheckOutDateException(Exception):

    def __init__(self, check_in, check_out, *args, **kwargs):
        super(CheckOutDateException, self).__init__(
            "Check-in Date: {} greater than Check-out Date \
            {}.".format(str(check_in), str(check_out)))


### MISC ###

class InvalidAmtException(Exception):
    pass

class ValidSenderException(Exception):
    pass

class PhoneNumberInUse(ValidationError):
    pass

class InvalidSubaccountStatus(Exception):
    pass
