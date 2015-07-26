String.prototype.trunc = String.prototype.trunc ||
    function (n) {
        return this.length > n ? this.substr(0, n - 1) + '&hellip;' : this;
    };

String.prototype.jsonify = function () {
    var n = this;
    for (var i in n) {
        n = n.replace("&#39;", '"');
        n = n.replace(': u"', ': "');
        n = n.replace("None", null);
    }
    return n;
};

$.validator.setDefaults({
    errorElement: "span",
    errorClass: "help-block",
    highlight: function (element, errorClass, validClass) {
        $(element).closest('.form-group, .form-group-sm, .form-group-lg').removeClass('has-success').addClass('has-error');
        $(element).attr('style', "border:rgb(217, 83, 79) 1px solid;");
    },
    unhighlight: function (element, errorClass, validClass) {
        $(element).closest('.form-group, .form-group-sm, .form-group-lg').removeClass('has-error').addClass('has-success');
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

// UI VALIDATION
$(document).ready(function () {
    jQuery.validator.addMethod("password", function (value, element) {
        return this.optional(element) || value.length >= 8;
    }, "Please use at least 8 characters.");
    jQuery.validator.addMethod("email", function (value, element) {
        return this.optional(element) || /^[A-Za-z0-9](([_\.\-]?[a-zA-Z0-9]+)*)@([A-Za-z0-9]+)(([\.\-]?[a-zA-Z0-9]+)*)\.([A-Za-z]{2,})$/i.test(value);
    }, "Please use a valid e-mail address.");
    jQuery.validator.addMethod("charField", function (value, element) {
        return this.optional(element) || /^([0-9a-zA-Z-_.~])+$/i.test(value);
    }, "Please use these special characters: - _ . ~");
    jQuery.validator.addMethod("ip", function (value, element) {
        return this.optional(element) || /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/i.test(value);
    }, "Please enter valid IP address.");
    jQuery.validator.addMethod("projectTag", function (value, element) {
        return value != "";
    }, "Tag cannot be blank to auto-fill form.");
});