String.prototype.trunc = String.prototype.trunc ||
    function (n) {
        return this.length > n ? this.substr(0, n - 1) + '&hellip;' : this;
    };

$.validator.setDefaults({
    errorElement: "span",
    errorClass: "help-block",
    highlight: function (element, errorClass, validClass) {
        $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
        $(element).attr('style', "border:rgb(217, 83, 79) 1px solid;");
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
        $(element).attr('style', "border:rgb(92, 184, 92) 1px solid;");
    },
    errorPlacement: function (error, element) {
        if (element.parent('.input-group').length || element.prop('type') === 'checkbox' || element.prop('type') === 'radio') {
            error.insertAfter(element.parent());
        } else {
            error.insertAfter(element);
        }
    }
});

$(document).ready(function () {
    jQuery.validator.addMethod("password", function (value, element) {
        return this.optional(element) || value.length >= 8;
    }, "Please use at least 8 characters");
    jQuery.validator.addMethod("charField", function (value, element) {
        return this.optional(element) || /([0-9a-zA-Z_])+$/i.test(value);
    }, "Please use letters, numbers and underscores(_)");
    jQuery.validator.addMethod("ip", function(value, element) {
        return this.optional(element) || /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/i.test(value);
    }, "Please enter valid IP address");
});