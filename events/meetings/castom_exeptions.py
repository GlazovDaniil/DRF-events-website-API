from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework import status


class MyCustomException(PermissionDenied):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Custom Exception Message"
    default_code = 'invalid'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class Http200Exception(APIException):
    status_code = status.HTTP_200_OK
    default_detail = "Удачно"
    default_code = 'OK'
