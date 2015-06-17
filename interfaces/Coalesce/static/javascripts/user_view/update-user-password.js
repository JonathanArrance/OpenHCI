$(function () {

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var password1 = $("#password1"),
        password2 = $("#password2"),
        allFields = $([]).add(password1).add(password2);

    $("#dialog-form-update-password").dialog({
        autoOpen: false,
        height: 275,
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

                clearUiValidation(allFields);

                var bValid =
                    checkPassword(password1) &&
                    checkPasswordMatch(password1, password2);

                if (bValid) {

                    $.getJSON('/update_user_password/' + USER_ID + '/' + password1.val() + '/' + PROJECT_ID + '/')
                        .done(function(data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);
                            }
                        })
                        .fail(function() {

                            message.showMessage('error', 'Server Fault');
                        });

                    $(this).dialog("close");
                }
            }
        },
        close: function () {
            resetUiValidation(allFields);
        }
    });

    $("#update-user-password")
        .click(function (event) {
            event.preventDefault();
            $("#dialog-form-update-password").dialog("open");
        });
});
