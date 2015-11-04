"""User specific properties to communicate with ASM."""

ASM_URL = 'http://172.24.24.10:8080/apkv/{path}'

COOKIE_NAME = 'trans-asm-py-d1a2n3c4e5%s%s'

LICENSE_KEY_USER = 'tc-user-084rjt24p3ohtwqrpoif'

#LICENSE_KEY_POWER_USER = 'aPAPI-TRANS-POWER-USER'
LICENSE_KEY_POWER_USER = 'tc-admin-084rjt24p3ohtwqrpoif'


class RequestAttributes(object):

  AUTH_PARAM = 'a'
  CLIENT_IP = 'uIp'
  COOKIE_VALUE = 'c'
  HOSTNAME = 'hName'
  ID = 'id'
  LICENSE_KEY = 'l'
  OTP = 'o'
  REQUEST_URL = 'wr'
  USERNAME = 'u'
