$(function () {

    // Widget Elements
    var progressbar = $("#users_progressbar"),
        table = $("#users_list"),
        placeholder = '<tr id="users_placeholder"><td><p><i>This project has no images</i></p></td><td></td></tr>';

    // --- Create ---

    $(function () {

        // Form Elements
        var name = $("#username"),
            email = $("#email"),
            password = $("#password"),
            confirm = $("#confirm"),
            role = $("#role"),
            allFields = $([]).add(name).add(email).add(password).add(confirm).add(role);

        $("#create-user").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#user-dialog-form").dialog("open");
        });

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
                        checkLength(name, "Username", standardStringMin, standardStringMax) &&
                        checkCharfield(name, "Username") &&
                        checkDuplicateName(name, users) &&
                        checkLength(email, "Email", 5, 80) &&
                        checkEmail(email) &&
                        checkPassword(password) &&
                        checkPasswordMatch(password, confirm);

                    if (isValid) {

                        // Confirmed Selections
                        var confName = name.val(),
                            confPassword = password.val(),
                            confEmail = email.val(),
                            confRole = role.val();

                        messages.showMessage('notice', 'Creating new user ' + name.val());

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

                                    messages.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    messages.showMessage('success', data.message);

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

                                messages.showMessage('error', 'Server Fault');
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
    });

    // --- Delete ---

    $(function () {

        // Local Variables
        var id,
            user,
            targetRow;

        $(document).on('click', '.delete-user', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            user = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#user-delete-confirm-form > p > span.user-name').empty().append($(user).text());

            $('#user-delete-confirm-form').dialog("open");
        });

        $('#user-delete-confirm-form').dialog({
            autoOpen: false,
            height: 125,
            width: 200,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confUsername = $(user).text();

                    messages.showMessage('notice', "Deleting " + confUsername + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and widgets actions
                    disableLinks(true);
                    disableActions("delete-user", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "users", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_user/' + confUsername + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                // Remove row
                                confRow.fadeOut().remove();

                                // Remove from users
                                users.removeItem(confUsername);

                                // If last user, reveal placeholder
                                var rowCount = $('#users_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                }
                            }
                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "users", true);
                            disableActions("delete-user", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Add Existing ---

    $(function () {

        // Form Elements
        var user = $("#username"),
            role = $("#role");

        $("#add-existing-user").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#user-add-existing-dialog-form").dialog("open");
        });

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

                    messages.showMessage('notice', 'Adding existing user ' + confUser + ".");

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

                                messages.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

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

                            messages.showMessage('error', 'Server Fault');
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
    });

    // --- Remove ---

    $(function () {

        // Local Variables
        var id,
            user,
            targetRow;

        $(document).on('click', '.remove-user', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            user = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#user-remove-confirm-form > p > span.user-name').empty().append($(user).text());
            $('#user-remove-confirm-form').dialog("open");
        });

        $('#user-remove-confirm-form').dialog({
            autoOpen: false,
            height: 125,
            width: 200,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confUsername = $(user).text();

                    messages.showMessage('notice', "Removing " + confUsername + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and widgets actions
                    disableLinks(true);
                    disableActions("remove-user", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "users", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/remove_user_from_project/' + confId + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                // Remove row
                                confRow.fadeOut().remove();

                                // Update users
                                users.items[confUsername].removed = "TRUE";

                                // Update select
                                addToSelect(confUsername, confUsername, $("select#username"), orphanedUserOpts);

                                // If last user, reveal placeholder
                                var rowCount = $('#users_list tr').length;
                                if (rowCount < 2) {
                                    table.append(placeholder).fadeIn();
                                }
                            }

                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "users", true);
                            disableActions("remove-user", false);
                            disableLinks(false);
                            checkAddUser();
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Enable ---
    $(function () {

        // Local Variables
        var id,
            user,
            targetRow;

        $(document).on('click', '.enable-user', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            user = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#user-enable-confirm-form > p > span.user-name').empty().append($(user).text());
            $("#user-enable-confirm-form").dialog("open");
        });

        $("#user-enable-confirm-form").dialog({
            autoOpen: false,
            height: 125,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confUsername = $(user).text();

                    messages.showMessage('notice', "Enabling " + confUsername + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and widgets actions
                    disableLinks(true);
                    disableActions("enable-user", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "users", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/toggle_user/' + confUsername + '/enable/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);

                                // Recall clicked action link on error
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                // Update status and actions cells
                                var newActions =
                                    '<a href="#" class="disable-user">disable</a>' +
                                    '<span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="remove-user">remove</a>' +
                                    '<span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-user"> delete</a>';

                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(newActions).fadeIn();

                                confRow.removeClass("user-disabled");
                            }
                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "users", true);
                            disableActions("enable-user", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                },
                close: function () {
                }
            }
        });
    });

    // --- Disable ---

    $(function () {

        // Local Variables
        var id,
            user,
            targetRow;

        $(document).on('click', '.disable-user', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            user = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#user-disable-confirm-form > p > span.user-name').empty().append($(user).text());
            $("#user-disable-confirm-form").dialog("open");
        });

        $("#user-disable-confirm-form").dialog({
            autoOpen: false,
            height: 125,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confRow = targetRow,
                        confId = id,
                        confUsername = $(user).text();

                    messages.showMessage('notice', "Disabling " + confUsername + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and widgets actions
                    disableLinks(true);
                    disableActions("disable-user", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "users", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/toggle_user/' + confUsername + '/disable/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                messages.showMessage('error', data.message);

                                // Recall clicked action link on error
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                messages.showMessage('success', data.message);

                                // Update status and actions cells
                                var newActions =
                                    '<a href="#" class="enable-user">enable</a>' +
                                    '<span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="remove-user">remove</a>' +
                                    '<span class="user-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-user"> delete</a>';

                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(newActions).fadeIn();

                                confRow.addClass("user-disabled");
                            }
                        })
                        .fail(function () {

                            messages.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "users", true);
                            disableActions("disable-user", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                },
                close: function () {
                }
            }
        });
    });
});