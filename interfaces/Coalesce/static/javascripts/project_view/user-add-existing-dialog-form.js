$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var name = $("#username"),
        role = $("#role");

    // Widget Elements
    var progressbar = $("#users_progressbar"),
        table = $("#users_list");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#user-add-existing-dialog-form").dialog({
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

                message.showMessage('notice', 'Adding existing user ' + name.text());

                setVisible('#add-existing-user', false);
                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                $.getJSON('/add_existing_user/' + name.val() + '/' + role.val() + '/' + PROJECT_ID + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);
                        }
                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Initialize empty string for new user row
                            var newRow = '';
                            newRow +=
                                '<tr id="' + data.user.user_id + '"';
                            if (data.user.user_enabled == "FALSE") {
                                newRow += ' class="user_disabled"'
                            }
                            newRow +=
                                '>' +
                                    '<td id="' + data.user.user_id + '-name-cell">' +
                                        '<a href="/projects/' + PROJECT + '/' + PROJECT_ID + '/user/' + data.user.username + '/view/" ' +
                                        'class="disable-link"><span id="' + data.user.user_id + '-name-text">' + data.user.username + '</span></a>' +
                                        '<a href="mailto:' + data.user.email + '">' +
                                            '<span id="' + data.user.user_id + '-email-text"> (' + data.user.email + ') </span></a>' +
                                        '<span id="' + data.user.user_id + '-role-text" class="right">' + data.user.user_role + '</span>' +
                                    '</td>' +
                                    '<td id="' + data.user.user_id + '-actions-cell">';
                            if (data.user.user_enabled == "TRUE") {
                                newRow +=
                                        '<a href="#" class="disable-user">disable</a>'
                            } else {
                                newRow +=
                                        '<a href="#" class="enable-user">enable</a>'
                            }
                            newRow +=
                                        '<span class="user-actions-pipe"> | </span>' +
                                        '<a href="#" class="remove-user">remove</a>' +
                                        '<span class="user-actions-pipe"> | </span>' +
                                        '<a href="#" class="delete-user"> delete</a>' +
                                    '</td>' +
                                '</tr>';

                            // Check to see if this is the first user to be generated, if so remove placeholder
                            var rowCount = $("#users_list tr").length;
                            if (rowCount >= 2) {
                                $("#users_placeholder").remove().fadeOut();
                            }

                            // Append new row to users_list
                            table.append(newRow).fadeIn();

                            unassignedUsers--;
                            var userSelect = 'div#user-add-existing-dialog-form > form > fieldset > select#username option[value=' + data.user.username + ']';
                            $(userSelect).remove();
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');
                    })
                    .always(function () {

                        // Check to see if this is the last unassigned user, if so remove add-existing-user
                        console.log(unassignedUsers);
                        if (unassignedUsers <= 0) {
                            setVisible("#add-existing-user", false);
                        } else {
                            setVisible('#add-existing-user', true);
                        }

                        setVisible(progressbar, false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#add-existing-user")
        .click(function () {
            $("#user-add-existing-dialog-form").dialog("open");
        });
});







