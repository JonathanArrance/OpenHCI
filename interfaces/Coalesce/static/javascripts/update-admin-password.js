$(function () {
    $("#update-admin-password")
        .click(function (event) {
            event.preventDefault();
            var form = $("<div></div>").prop("id", "dialog-form-update-password").prop("title", "Update Password")
                    .append($("<p>All form fields are required.</p>").addClass("validateTips"))
                    .append($("<form></form>")
                        .append($("<fieldset></fieldset>")
                            .append($("<label>Current Password</label>").prop("for", "password0"))
                            .append($("<input></input>").prop("type", "password").prop("name", "password0").prop("id", "password0").addClass("text"))
                            .append($("<label>New Password</label>").prop("for", "password1"))
                            .append($("<input></input>").prop("type", "password").prop("name", "password1").prop("id", "password1").addClass("text"))
                            .append($("<label>Confirm New Password</label>").prop("for", "password2"))
                            .append($("<input></input>").prop("type", "password").prop("name", "password2").prop("id", "password2").addClass("text"))));
            var allFields = $([]);
            form.dialog({
                autoOpen: true,
                height: 315,
                width: 235,
                modal: true,
                resizable: false,
                closeOnEscape: true,
                draggable: true,
                show: "fade",
                position: {
                    my: "top",
                    at: "center",
                    of: $('#page-content')
                },
                buttons: {
                    "Update Password": function () {
                        var password0 = $("#password0"),
                            password1 = $("#password1"),
                            password2 = $("#password2");
                        allFields.add(password0).add(password1).add(password2);
                        clearUiValidation(allFields);
                        var bValid = checkPassword(password1) && checkPasswordMatch(password1, password2);
                        if (bValid) {
                            $.getJSON('/update_admin_password/' + password0.val() + '/' + password1.val() + '/')
                                .done(function (data) {
                                    if (data.status == 'error') {
                                        message.showMessage('error', data.message);
                                    }
                                    if (data.status == 'success') {
                                        message.showMessage('success', data.message);
                                    }
                                })
                                .fail(function () {
                                    message.showMessage('error', 'Server Fault');
                                });
                            $(this).remove();
                        }
                    }
                },
                close: function () {
                    var password1 = $("#password1"),
                        password2 = $("#password2"),
                        password0 = $("#password0");
                    allFields.add(password0).add(password1).add(password2);
                    resetUiValidation(allFields);
                }
            });
        });
});


