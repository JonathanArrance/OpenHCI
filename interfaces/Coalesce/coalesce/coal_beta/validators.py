from django.core.exceptions import ValidationError
import re

def validate_percentage(value):
    if 0 > value or value > 100:
        raise ValidationError(u'%s is not a valid percentage.  Please enter a number from 0-100.' % value)


def validate_ppm(value):
    if 0 > value or value > 1000000:
        raise ValidationError(
            u'%s is not a valid part per million.  Please enter a number from 0 to 1 million.' % value)


def validate_charfield(value):
    try:
        if not re.match("([0-9a-zA-Z_])+$", value):
            raise ValidationError(u'This field may consist of letters, numbers and underscores.')
    except:
        raise ValidationError(u'This field may consist of letters, numbers and underscores.')
