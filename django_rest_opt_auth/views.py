from smssender import SMSSender
import jwt
from django.http.response import JsonResponse
from http import HTTPStatus
import json
from json import JSONDecodeError
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta
import string
import random
from django.core.exceptions import ObjectDoesNotExist
from django.utils.module_loading import import_string


def create_jwt(user):
    token = jwt.encode({
        'role': settings.JWT_ROLE,
        'userid': str(user.id),
        'exp': (datetime.now() + timedelta(minutes=settings.JWT_EXP)).timestamp(),
    }, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {'token': token}


class SmsErrors:
    WRONG_DATA_FORMAT = 'Incorrect data format, JSON expected'

    PHONE_REQUIRED = "'phone' field is required"
    CODE_REQUIRED = "'code' field is required"

    USER_NOT_FOUND = 'User not found'

    POST_JSON = 'Only POST method, only JSON data'


def prepare_response(status: int, token=None, error=None, message=None):
    resp = {'status': status}
    if error:
        resp['data'] = {'error': {'message': error}}
    elif token:
        if isinstance(token, dict):
            resp['data'] = token
        elif isinstance(token, str):
            resp['data'] = {'token': token}
    elif message:
        resp['data'] = {'message': message}
    resp['data']['status'] = status
    return resp


def generate_short_code(n, l=None, u=None, d=None):
    if n <= 0:
        n = 1
    array = ''
    if l:
        array += string.ascii_lowercase
    if u:
        array += string.ascii_uppercase
    if d:
        array += string.digits
    if not l and not u and not d:
        array = string.ascii_letters + string.digits
    return ''.join(random.choice(array) for i in range(n))


def send_sms(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse(**prepare_response(status=HTTPStatus.BAD_REQUEST, error=SmsErrors.WRONG_DATA_FORMAT))

        tel_number = request_body.get('phone')
        if not tel_number:
            return JsonResponse(**prepare_response(status=HTTPStatus.BAD_REQUEST, error=SmsErrors.PHONE_REQUIRED))

        try:
            user = get_user_model().objects.get(phone_number=tel_number)
        except ObjectDoesNotExist:
            return JsonResponse(**prepare_response(status=HTTPStatus.NOT_FOUND, error=SmsErrors.USER_NOT_FOUND))

        code = generate_short_code(settings.SMS_CODE_LEN, l=settings.SMS_CODE_LOWER, u=settings.SMS_CODE_UPPER,
                                   d=settings.SMS_CODE_DIGITS)

        config = {
            'to': tel_number,
            'body': settings.OTP_MESSAGE.format(APP_NAME=settings.APP_NAME, CODE=code),
            'TWILIO_SID': settings.TWILIO_SID,
            'TWILIO_TOKEN': settings.TWILIO_TOKEN,
            'TWILIO_NUMBER': settings.TWILIO_NUMBER
        }

        driver = import_string(settings.SMS_DRIVER)

        result = SMSSender(driver, config).send()
        if isinstance(result, tuple):
            return JsonResponse(**prepare_response(status=result[0], error=result[1]))

        result = {
            'from': result.from_,
            'to': result.to,
            'status': result.status
        }
        user.short_code = code
        user.save()

        return JsonResponse(**prepare_response(status=HTTPStatus.OK, message=result))
    return JsonResponse(**prepare_response(status=HTTPStatus.METHOD_NOT_ALLOWED, error=SmsErrors.POST_JSON))


def check_sms(request):
    if request.method == 'POST':
        try:
            request_body = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse(**prepare_response(status=HTTPStatus.BAD_REQUEST, error=SmsErrors.WRONG_DATA_FORMAT))

        code = request_body.get('code')
        if not code:
            return JsonResponse(**prepare_response(status=HTTPStatus.BAD_REQUEST, error=SmsErrors.CODE_REQUIRED))

        try:
            user = get_user_model().objects.get(short_code=code)
        except ObjectDoesNotExist:
            return JsonResponse(**prepare_response(status=HTTPStatus.NOT_FOUND, error=SmsErrors.USER_NOT_FOUND))

        user.short_code = None
        return JsonResponse(**prepare_response(status=HTTPStatus.OK, token=create_jwt(user)))
    return JsonResponse(**prepare_response(status=HTTPStatus.METHOD_NOT_ALLOWED, error=SmsErrors.POST_JSON))
