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
                'single_node',
            HTML('</div>'),
            HTML('</div>'),
            HTML('<div class="offset1">'),

            Submit('cancel', 'Cancel Setup', css_class='btn-warning'),
            Submit('submit', 'Setup Box'),

            HTML('</div>'),
        )

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
        self.helper.layout = Layout(
            HTML('<div class="row">'),
            
            HTML('<div class="well span5  offset1"><div class="legend">Security Settings</div>'),
                'proj_name',
                'group_name',
                'group_desc',
                'sec_keys_name',
            HTML('</div>'),
            
            HTML('<div class="well span5"><div class="legend">Power User Settings</div>'),
                'username',
                'email',
                'password',
                'password_confirm',
            HTML('</div>'),
            HTML('</div>'),
            
            HTML('<div class="row">'),
            HTML('<div class="well span5  offset1"><div class="legend">Software Defined Network Settings</div>'),
                'router_name',
                'net_name',
                'subnet_dns',
            HTML('</div>'),
            
            HTML('</div>'),
            HTML('<div class="offset1">'),

            Submit('cancel', 'Cancel', css_class='btn-warning'),
            Submit('submit', 'Create Project'),

            HTML('</div>'),
        )


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

