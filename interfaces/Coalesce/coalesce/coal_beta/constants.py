AUTH_PARAM = ''

IP_HEADERS_ORDERED = (
  'HTTP_X_CLIENT_IP',
  'HTTP_X_FORWARDED_FOR',
  'HTTP_X_FORWARDED',
  'HTTP_CLIENT_IP',
  'HTTP_FORWARDED_FOR',
  'HTTP_FORWARDED',
  'REMOTE_ADDR')


class UserLevel(object):
  DEFAULT_USER = 0
  POWER_USER = 1
