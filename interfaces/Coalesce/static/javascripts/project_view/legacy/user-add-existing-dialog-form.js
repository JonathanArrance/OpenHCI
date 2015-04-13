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
    var user = $("#username"),
        role = $("#role");

    // Widget Elements
    var progressbar = $("#users_progressbar"),
        table = $("#users_list");

    $("#user-add-existing-dialog-form").dialog({
        autoOpen: false,
        height: 300,
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
            "Add Existing User": function () {

                // Confirmed Selections
                var confUser = user.val(),
                    confRole = role.val();

                message.showMessage('notice', 'Adding existing user ' + confUser + ".");

                // Hide widget buttons and disable widget view links
                setVisible("#create-user", false);
                setVisible("#add-existing-user", false);
                disableLinks(true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "users", false);

                $.getJSON('/add_existing_user/' + confUser + '/' + confRole + '/' + PROJECT_ID + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Update user
                            users.items[confUser].removed = "FALSE";
                            users.items[confUser].role = confRole;

                            // Initialize empty string for new user row
                            var newRow = '<tr id="' + users.items[confUser].id + '" class="';
                            if (users.items[confUser].enabled == "FALSE") {
                                newRow += 'user-disabled">';
                            } else {
                                newRow += '">';
                            }
                            newRow +=
                                '<td id="' + users.items[confUser].id + '-name-cell">' +
                                '<a href="/projects/' + PROJECT + '/' + PROJECT_ID + '/user/' + users.items[confUser].username + '/view/" ' +
                                'class="disable-link"><span id="' + users.items[confUser].id + '-name-text">' + users.items[confUser].username + '</span></a>' +
                                '<a href="mailto:' + users.items[confUser].email + '">' +
                                '<span id="' + users.items[confUser].id + '-email-text"> (' + users.items[confUser].email + ') </span></a>' +
                                '<span id="' + users.items[confUser].id + '-role-text" class="right">' + users.items[confUser].role + '</span>' +
                                '</td>' +
                                '<td id="' + users.items[confUser].id + '-actions-cell">';
                            if (users.items[confUser].enabled == "TRUE") {
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

                            // Append new row to users_list
                            table.append(newRow).fadeIn();

                            // Check to see if this is the first user to be generated, if so remove placeholder
                            var rowCount = $("#users_list tr").length;
                            if (rowCount >= 2) {
                                $("#users_placeholder").remove().fadeOut();
                            }

                            // Update select
                            removeFromSelect(confUser, $("select#username"), orphanedUserOpts);
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
                        checkAddUser();
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#add-existing-user")
        .click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#user-add-existing-dialog-form").dialog("open");
        });
});







