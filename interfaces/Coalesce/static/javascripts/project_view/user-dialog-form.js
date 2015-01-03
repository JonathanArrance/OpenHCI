$(function () {

    // CSRF Protection
    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Form Elements
    var name = $("#username"),
        email = $("#email"),
        password = $("#password"),
        confirm = $("#confirm"),
        role = $("#role"),
        allFields = $([]).add(name).add(email).add(password).add(confirm).add(role);

    // Widget Elements
    var progressbar = $("#users_progressbar"),
        table = $("#users_list");

    $("#user-dialog-form").dialog({
        autoOpen: false,
        height: 475,
        width: 235,
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
            "Create Account": function () {

                // Remove UI validation flags
                clearUiValidation(allFields);

                var isValid =
                    checkLength(name, "username", 3, 16) &&
                    checkUsername(name) &&
                    checkDuplicateName(name, users) &&
                    checkLength(email, "email", 6, 80) &&
                    checkEmail(email) &&
                    checkLength(password, "password", 5, 16) &&
                    checkPassword(password) &&
                    checkPasswordMatch(password, confirm);

                if (isValid) {

                    // Confirmed Selections
                    var confName = name.val(),
                        confPassword = password.val(),
                        confEmail = email.val(),
                        confRole = role.val();

                    message.showMessage('notice', 'Creating new user ' + name.val());

                    // Hide widget buttons and disable widget view links
                    setVisible("#create-user", false);
                    setVisible("#add-existing-user", false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "users", false);

                    $.getJSON('/create_user/' + confName + '/' + confPassword + '/' + confRole + '/' + confEmail + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new router row
                                var newRow = '';
                                newRow +=
                                    '<tr id="' + data.user_id + '"><td id="' + data.user_id + '-name-cell">' +
                                    '<a href="/projects/' + PROJECT + '/' + PROJECT_ID + '/user/' + data.username + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.user_id + '-name-text">' + confName + '</span></a>' +
                                    '<a href="mailto:' + confEmail + '"><span id="' + data.user_id + '-email-text"> (' + confEmail + ')</span></a>' +
                                    '<span id="' + data.user_id + '-role-text"> ' + confRole + '</span></td>' +
                                    '<td id="' + data.user_id + '-actions-cell">' +
                                    '<a href="#" class="disable-user">disable</a><span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="remove-user">remove</a><span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-user">delete</a></td></tr>';

                                // Check to see if this is the first router to be generated, if so remove placeholder and reveal delete-router button
                                var rowCount = $("#users_list tr").length;
                                if (rowCount <= 2) {
                                    $("#users_placeholder").remove().fadeOut();
                                }

                                // Append new row to router-list
                                table.append(newRow).fadeIn();

                                users.setItem(
                                    data.username,
                                    { id: data.user_id, enabled: "TRUE", username: data.username,
                                        email: confEmail, role: confRole, removed: "FALSE" }
                                );
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            disableProgressbar(progressbar, "users", true);
                            setVisible("#create-user", true);
                            disableLinks(false);
                            resetUiValidation(allFields);
                            checkAddUser();
                        });

                    $(this).dialog("close");
                }
            }
        },
        close: function () {

            // Reset form validation
            resetUiValidation(allFields);
        }
    });

    $("#create-user")
        .click(function () {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#user-dialog-form").dialog("open");
        });
});
