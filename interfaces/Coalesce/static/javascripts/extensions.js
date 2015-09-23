String.prototype.jsonify = function () {
    var n = this;
    for (var i in n) {
        n = n.replace("&#39;", '"');
        n = n.replace(': u"', ': "');
        n = n.replace(', u"', ', "');
        n = n.replace('{u"', '{"');
        n = n.replace("None", null);
    }
    return n;
};

String.prototype.slashTo47 = function () {
    return this.replace(/\//g, '&47');
};

String.prototype.testPorts = function () {
    var ports = this.trim().split(","),
        errorString = "";
    $(ports).each(function (index, port) {
        if (port == "") {
            errorString = "Formatting error, please check your input.";
            return false;
        } else if (port.search("-") != -1) {
            var rangeArray = port.split("-");
            if (rangeArray.length != 2) {
                errorString = port + " is not a valid range.";
                return false;
            } else if (!(parseInt(rangeArray[0]) && rangeArray[0] > 0 && rangeArray[0] <= 65535)) {
                errorString = rangeArray[0] + " is not a valid port.";
                return false;
            } else if (!(parseInt(rangeArray[1]) && rangeArray[1] > 0 && rangeArray[1] <= 65535)) {
                errorString = rangeArray[1] + " is not a valid port.";
                return false;
            } else if (rangeArray[0] >= rangeArray[1]) {
                errorString = port + " is not a valid range.";
                return false;
            } else {
                errorString = "";
                return true;
            }
        } else if (!(parseInt(port) && port > 0 && port <= 65535)) {
            errorString = port + " is not a valid port.";
            return false;
        } else {
            errorString = "";
            return true;
        }
    });
    return errorString == "" ? true : errorString;
};

String.prototype.formatPorts = function () {
    if (!this.testPorts()) return "error";
    var ports = this.trim().split(","),
        returnString = "";
    $(ports).each(function (index, port) {
        returnString += port.search("-") == -1 ? port.trim() : port.split("-")[0].trim() + "-" + port.split("-")[1].trim();
        if ((index + 1) < ports.length) returnString += ",";
    });
    return returnString;
};

Number.prototype.between = function (min, max) {
    return this > min && this < max;
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
    errorString = "";
    jQuery.validator.addMethod("passwordCreate", function (value, element) {
        return this.optional(element) || value.length >= 8;
    }, "Please use at least 8 characters.");
    jQuery.validator.addMethod("email", function (value, element) {
        return this.optional(element) || /^[A-Za-z0-9](([_\.\-]?[a-zA-Z0-9]+)*)@([A-Za-z0-9]+)(([\.\-]?[a-zA-Z0-9]+)*)\.([A-Za-z]{2,})$/i.test(value);
    }, "Please use a valid e-mail address.");
    jQuery.validator.addMethod("charField", function (value, element) {
        return this.optional(element) || /^([0-9a-zA-Z-_.~])+$/i.test(value);
    }, "Please use these characters: - _ . ~");
    jQuery.validator.addMethod("specialChars", function (value, element) {
        return this.optional(element) || !/([!])|([*])|([(])|([)])|(['])/g.test(value);
    }, "Please replace these characters: ! * ( )'");
    jQuery.validator.addMethod("ip", function (value, element) {
        return this.optional(element) || /^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/i.test(value);
    }, "Please enter valid IP address.");
    jQuery.validator.addMethod("projectTag", function (value, element) {
        return value != "";
    }, "Tag cannot be blank to auto-fill form.");
    jQuery.validator.addMethod("file", function (value, element) {
        return value != "";
    }, "Please select a file.");
    jQuery.validator.addMethod("remote", function (value, element) {
        return value != "";
    }, "Please enter a remote url.");
    jQuery.validator.addMethod("port", function (value, element) {
        return this.optional(element) || /^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$/i.test(value);
    }, "Please use a valid port: 0 to 65535.");
    jQuery.validator.addMethod("ports", function (value, element) {
        if (!this.optional(element)) {
            errorString = value.toString().testPorts();
        } else {
            if (value == "") return true;
            errorString = value.toString().testPorts();
        }
        return errorString == true;
    }, function () {
        return errorString;
    });
});