from django.core.exceptions import ValidationError

def validate_percentage(value):
    if 0 > value or value > 100:
        raise ValidationError(u'%s is not a valid percentage.  Please enter a number from 0-100.' % value)
        
def validate_ppm(value):
    if 0 > value or value > 1000000:
        raise ValidationError(u'%s is not a valid part per million.  Please enter a number from 0 to 1 million.' % value)

        
        