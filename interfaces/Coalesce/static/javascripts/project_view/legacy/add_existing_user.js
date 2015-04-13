$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var name = $("#username"),
        role = $("#role"),
        allFields = $([]).add(name).add(role),
        tips = $(".validateTips");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#dialog-form-add-existing-user").dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        buttons: {
            "Add Existing User": function () {

                var bValid = true;

                allFields.removeClass("ui-state-error");
                $(".error").fadeOut.remove();

                bValid =
                    bValid &&
                    checkLength(name, "username", 3, 16) &&
                    checkRegexp(
                        tips,
                        name,
                        /^[a-z]([0-9a-z_])+$/i,
                        "Username may consist of a-z, 0-9, underscores, begin with a letter.");

                if (bValid) {

                    message.showMessage('notice', 'Adding existing user ' + name.text());

                    setVisible('#add-existing-user', false);
                    disableLinks(true);

                    $.getJSON('/add_existing_user/' + name.val() + '/' + role.val() + '/' + PROJECT_ID + '/')
                        .done(function () {
                            location.reload();
                        });

                    setVisible('#add-existing-user', true);
                    disableLinks(false);

                    $(this).dialog("close");

                    allFields.val("").removeClass("ui-state-error");
                    $(".error").fadeOut().remove();
                }
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
            $(".error").fadeOut().remove();
        }
    });

    $("#add-existing-user")
        .click(function () {
            $("#dialog-form-add-existing-user").dialog("open");
        });
});







