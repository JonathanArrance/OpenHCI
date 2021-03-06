from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django import forms
from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.utils.safestring import mark_safe
from validators import validate_charfield

BOOLEAN_CHOICES = (('False', 'No',), ('True', 'Yes',))

class SetupForm(forms.Form):

    management_ip = forms.IPAddressField(label = 'Management IP Address', help_text = 'IPv4 Ip address for the management network.')
    uplink_ip = forms.IPAddressField(label = 'Uplink IP Address', help_text = 'IPv4 Ip address for the uplink.')
    vm_ip_min = forms.IPAddressField(label = 'Virtual Machine IP Address Range (Minimum)', help_text = 'VMs will be allowed to use addresses between this and the maximum, inclusive.')
    vm_ip_max = forms.IPAddressField(label = 'Virtual Machine IP Address Range (Maximum)')
    uplink_dns = forms.IPAddressField(label = 'Uplink DNS')
    uplink_gateway = forms.IPAddressField(label = 'Uplink Gateway')
    uplink_domain_name = forms.CharField(min_length = 1, max_length = 64, label='Uplink Domain Name')
    uplink_subnet = forms.IPAddressField(label = 'Uplink Subnet')
    mgmt_domain_name  = forms.CharField(min_length = 1, max_length = 64, label='Management Domain Name')
    mgmt_subnet = forms.IPAddressField(label = 'Management Subnet')
    mgmt_dns  = forms.IPAddressField(label = 'Management DNS')
    admin_password = forms.CharField(widget=forms.PasswordInput(),  label='Administrator Password')
    admin_password_confirm = forms.CharField(widget=forms.PasswordInput(),  label='Administrator Password Confirm')

    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.help_text_inline = True
        self.helper.error_text_inline = False
        
        self.helper.layout = Layout(
            HTML('<div class="row">'),
            
            HTML('<div class="well span5  offset1"><div class="legend">Management Settings</div>'),
                'management_ip',
                'mgmt_subnet',
                'mgmt_dns',
                'mgmt_domain_name',
            HTML('</div>'),
            
            HTML('<div class="well span5"><div class="legend">Uplink Settings</div>'),
                'uplink_ip',
                'uplink_subnet',
                'uplink_dns',
                'uplink_domain_name',
                'uplink_gateway',
            HTML('</div>'),
            HTML('</div>'),
            
            HTML('<div class="row">'),
            HTML('<div class="well span5  offset1"><div class="legend">Virtual Machine Range</div>'),
                'vm_ip_min',
                'vm_ip_max',
            HTML('</div>'),
            
            HTML('<div class="well span5"><div class="legend">Global settings</div>'),
                'admin_password',
                'admin_password_confirm',
            HTML('</div>'),
            HTML('</div>'),
            HTML('<div class="offset1">'),

            Submit('cancel', 'Cancel Setup', css_class='btn-warning'),
            Submit('submit', 'Setup Box'),

            HTML('</div>'),
        )

class import_image_form(forms.Form):
    image = forms.FileField(label='Select an image to import')
