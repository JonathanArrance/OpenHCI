from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django import forms
from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.utils.safestring import mark_safe

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
    cloud_name  = forms.SlugField(min_length = 1, max_length = 64, label='Cloud Name', help_text = 'This is the region used in the OpenStack projects.')
    single_node = forms.BooleanField( label='Single Node?', help_text = 'If unchecked, this box will be setup with DHCP and listen for additional nodes to be added.  Check the box to improve performance if you do not plan to add nodes to this box.')
    admin_password = forms.CharField(widget=forms.PasswordInput(),  label='Administrator Password')
    admin_password_confirm = forms.CharField(widget=forms.PasswordInput(),  label='Administrator Password Confirm')

    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.help_text_inline = True
        self.helper.error_text_inline = False
        self.helper.add_input(Submit('cancel', 'Cancel Setup', css_class='btn-cancel'))
        self.helper.add_input(Submit('submit', 'Setup Box'))

class BuildProjectForm(forms.Form):
    proj_name = forms.SlugField(min_length = 1, max_length = 64, label='Project Name')
    username = forms.SlugField(min_length = 1, max_length = 64, label='Power User Name')
    password = forms.CharField(widget=forms.PasswordInput(),  label='Power User Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput(),  label='Power User Password Confirm')
    email = forms.EmailField( label='Power User email')
    net_name = forms.SlugField(min_length = 1, max_length = 64, label='Network Name')
    subnet_dns = forms.IPAddressField(label = 'Subnet DNS')
    #ports[] - op
    group_name = forms.SlugField(min_length = 1, max_length = 64, label='Security Group Name')
    group_desc = forms.CharField(min_length = 1, max_length = 64, label='Security Group Description')
    sec_keys_name = forms.SlugField(min_length = 1, max_length = 64, label='Security Key Name')
    router_name = forms.SlugField(min_length = 1, max_length = 64, label='Router Name')

    def __init__(self, *args, **kwargs):
        super(BuildProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.help_text_inline = True
        self.helper.error_text_inline = False
        self.helper.add_input(Submit('cancel', 'Cancel', css_class='btn-cancel'))
        self.helper.add_input(Submit('submit', 'Submit'))


class authentication_form(forms.Form):

    username  = forms.CharField(min_length = 2, max_length = 64, label='User Name')
    password = forms.CharField(widget=forms.PasswordInput(),  label='Password')


    def __init__(self, *args, **kwargs):
        super(authentication_form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.help_text_inline = True
        self.helper.error_text_inline = False
        self.helper.add_input(Submit('submit', 'Login'))

