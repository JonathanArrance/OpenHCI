$(function () {

    // Widget Elements
    var progressbar = $("#instance_progressbar"),
        table = $("#instance_list"),
        placeholder =
            '<tr id="instance_placeholder"><td><p><i>This project has no instances</i></p></td><td></td><td></td><td></td></tr>';

    // --- Create ---

    $(function () {

        // Form Elements
        var name = $("#name"),
            secGroupName = $("#sec_group_name"),
            secKeyName = $("#sec_key_name"),
            networkName = $("#network_name"),
            imageName = $("#image_name"),
            flavorName = $("#flavor_name"),
            allFields = $([]).add(secGroupName).add(secKeyName).add(imageName).add(name).add(networkName);

        $("#create-instance").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#instance-dialog-form").dialog("open");
        });

        $("#instance-dialog-form").dialog({
            autoOpen: false,
            height: 505,
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
                "Create Instance": function () {

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    // Validate form inputs
                    var isValid =
                        checkLength(name, "Instance Name", 3, 16) &&
                        checkDuplicateName(name, instanceOpts);

                    if (isValid) {

                        // Confirmed Selections
                        var confName = name.val(),
                            confSecGroup = secGroupName.val(),
                            confSecKey = secKeyName.val(),
                            confNetwork = networkName.val(),
                            confImage = imageName.val(),
                            confFlavor = flavorName.val();

                        message.showMessage('notice', 'Creating New Instance ' + confName);

                        // Hide widget buttons and disable widget view links
                        setVisible('#create-instance', false);
                        disableLinks(true);

                        // Initialize progressbar and make it visible if hidden
                        $(progressbar).progressbar({value: false});
                        disableProgressbar(progressbar, "instances", false);

                        $.getJSON('/create_image/' + confName + '/' + confSecGroup + '/nova/' + confFlavor + '/' + confSecKey + '/' + confImage + '/' + confNetwork + '/' + PROJECT_ID + '/')
                            .done(function (data) {

                                if (data.status == 'error') {

                                    message.showMessage('error', data.message);
                                }

                                if (data.status == 'success') {

                                    message.showMessage('success', data.message);

                                    // Generate HTML for new row
                                    var newRow =
                                        '<tr id="' + data.server_info.server_id + '"><td id="' + data.server_info.server_id + '-name-cell">' +
                                        '<a href="/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/" class="disable-link disabled-link" style="color:#696969;">' +
                                        '<span id="' + data.server_info.server_id + '-name-text">' + data.server_info.server_name + '</span></a></td>' +
                                        '<td id="' + data.server_info.server_id + '-status-cell">' + data.server_info.server_status + '</td>' +
                                        '<td id="' + data.server_info.server_id + '-os-cell">' + data.server_info.server_os + ' / ' + data.server_info.server_flavor + '</td>' +
                                        '<td id="' + data.server_info.server_id + '-actions-cell">';

                                    if (data.server_info.server_status == "ACTIVE") {

                                        newRow +=
                                            '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>' +
                                            '<span class="instance-actions-pipe"> | </span>' +
                                            '<a href="#" class="pause-instance ' + data.server_info.server_id + '-disable-action">pause</a><span class="instance-actions-pipe"> | </span>' +
                                            '<a href="#" class="suspend-instance ' + data.server_info.server_id + '-disable-action">suspend</a>';
                                    }

                                    if (data.server_info.server_status == "PAUSED") {

                                        newRow +=
                                            '<a href="#" class="unpause-instance ' + data.server_info.server_id + '-disable-action">unpause</a>';
                                    }

                                    if (data.server_info.server_status == "SUSPENDED") {

                                        newRow +=
                                            '<a href="#" class="resume-instance ' + data.server_info.server_id + '-disable-action">resume</a>';
                                    }

                                    newRow +=
                                        '<span class="instance-actions-pipe"> | </span><a href="#" class="delete-instance ' + data.server_info.server_id + '-disable-action">delete</a></td></tr>';

                                    // Check table length, remove placeholder if necessary
                                    var rowCount = $('#instance_list tr').length;
                                    if (rowCount >= 2) {
                                        $('#instance_placeholder').remove().fadeOut();
                                        setVisible("#create-instance-snapshot", true);
                                    }

                                    // Append new row to instance-list
                                    $(table).append(newRow).fadeIn();

                                    // Add to instances
                                    instances.setItem(
                                        data.server_info.server_id,
                                        {
                                            id: data.server_info.server_id,
                                            name: data.server_info.server_name,
                                            status: data.server_info.server_status,
                                            flavor: data.server_info.server_flavor,
                                            os: data.server_info.server_os,
                                            console: data.server_info.novnc_console
                                        }
                                    );
                                    consoleLinks.setItem(
                                        data.server_info.server_id,
                                        {
                                            link: data.server_info.novnc_console,
                                            html: '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>'
                                        }
                                    );

                                    // Update selects
                                    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance"), attachableInstances);
                                    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#assign_instance"), assignableInstances);
                                    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance_to_snap"), instanceOpts);
                                }
                            })
                            .fail(function () {

                                message.showMessage('error', 'Server Fault');
                            })
                            .always(function () {

                                // Reset interface
                                checkAssignFip();
                                disableProgressbar(progressbar, "instances", true);
                                setVisible('#create-instance', true);
                                disableLinks(false);
                                resetUiValidation(allFields);
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
            instance,
            targetRow;

        $(document).on('click', '.delete-instance', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            instance = document.getElementById(id + "-name-text");

            // Add name-text to form
            $('div#instance-delete-confirm-form > p > span.instance-name').empty().append($(instance).text());

            $('#instance-delete-confirm-form').dialog("open");
        });

        $("#instance-delete-confirm-form").dialog({
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
                        confInstance = $(instance).text();

                    message.showMessage('notice', "Deleting " + confInstance + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("delete-instance", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/delete_server/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Remove row
                                $(confRow).fadeOut().remove();

                                // Update selects
                                removeFromSelect(confId, $("#instance"), attachableInstances);
                                removeFromSelect(confId, $("#assign_instance"), assignableInstances);

                                if (assignableFips.length <= 0 || assignableInstances.length <= 0) {
                                    setVisible('#assign_ip', false);
                                }

                                // Unattach volumes
                                for (var i = 0; i < data.vols.length; i++) {

                                    var volAttachedCell = document.getElementById(data.vols[i] + '-attached-cell');
                                    $(volAttachedCell).empty().fadeOut();
                                    $(volAttachedCell).parent().removeClass("volume-attached");
                                    var newAttached = '<span id="' + data.vols[i] + '-attached-placeholder">No Attached Instance</span>';
                                    $(volAttachedCell).append(newAttached).fadeIn();

                                    var volActionsCell = document.getElementById(data.vols[i] + '-actions-cell');
                                    $(volActionsCell).empty().fadeOut();
                                    var newVolAction = '<a href="#" class="attach-volume">attach</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="clone-volume">clone</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="revert-volume">revert</a>' +
                                        '<span class="volume-actions-pipe"> | </span><a href="#" class="delete-volume">delete</a>';
                                    $(volActionsCell).append(newVolAction).fadeIn();

                                    snapshotVolumes.setItem(data.vols[i], { value: data.vols[i], option: volumes.items[data.vols[i]].name })
                                }

                                // Unassign floating IPs
                                for (var j = 0; j < data.floating_ip.length; j++) {

                                    var ipInstanceCell = document.getElementById(data.floating_ip_id[j] + '-instance-cell');
                                    $(ipInstanceCell).empty().fadeOut();
                                    $(ipInstanceCell).parent().removeClass("fip-assigned");
                                    var newInstance = '<span id="' + data.floating_ip[j] + '-instance-name">None</span>';
                                    $(ipInstanceCell).append(newInstance).fadeIn();

                                    var ipActionsCell = document.getElementById(data.floating_ip_id[j] + '-actions-cell');
                                    $(ipActionsCell).empty().fadeOut();
                                    var newIpAction = '<a id="' + data.floating_ip_id[j] + '" class="deallocate_ip" href="#">deallocate</a>';
                                    $(ipActionsCell).append(newIpAction).fadeIn();

                                    console.log(fips);
                                    console.log(data.floating_ip_id[j]);
                                    assignableFips.setItem(data.floating_ip_id[j], { value: data.floating_ip_id[j], option: fips.getItem(data.floating_ip_id[j]).ip })
                                }

                                // Remove from instances
                                instances.removeItem(confId);
                                instanceOpts.removeItem(confId);

                                // Update Selects
                                refreshSelect('#instance_to_snap', instanceOpts);
                                refreshSelect($("#bam-security-ip"), assignableFips);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Attaching IP")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-security-ip"));
                                refreshSelect("#bam-volume-select-existing", snapshotVolumes);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Adding Storage")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-volume-select-existing"));
                                $('<option></option>')
                                    .val("create")
                                    .html("Create Volume")
                                    .appendTo($("#bam-volume-select-existing"));

                                // If last row, append placeholder
                                var rowCount = $('#instance_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                    setVisible("#create-instance-snapshot", false);
                                }
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            checkAssignFip();
                            disableProgressbar(progressbar, "instances", true);
                            disableActions("delete-instance", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Pause ---

    $(function () {

        // Local Variables
        var id,
            instance,
            targetRow;

        $(document).on('click', '.pause-instance', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the instance-name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            instance = document.getElementById(id + "-name-text");

            // Add instance-name-text to confirm-form
            $('div#instance-pause-confirm-form > p > span.instance-name').empty().append($(instance).text());

            $("#instance-pause-confirm-form").dialog("open");
        });

        $("#instance-pause-confirm-form").dialog({
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
                    var confId = id,
                        confInstance = $(instance).text();

                    message.showMessage('notice', "Pausing " + confInstance + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("pause-instance", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/pause_server/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var statusCell = document.getElementById(confId + "-status-cell");

                                // Update status cell
                                $(statusCell).fadeOut().empty();
                                $(statusCell).append("PAUSED").fadeIn();

                                // Create new actions
                                var newActions =
                                    '<a href="#" class="unpause-instance ' + confId + '-disable-action">unpause</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                                // Update actions-cell
                                $(actionsCell).fadeOut().empty();
                                $(actionsCell).append(newActions).fadeIn();

                                // Add paused class
                                $(targetRow).addClass("instance-paused");

                                // Update instance
                                instances.items[confId].status = "PAUSED";
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar, enabled instance actions and widget view links
                            disableProgressbar(progressbar, "instances", true);
                            disableActions("pause-instance", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Unpause ---

    $(function () {

        // Local Variables
        var id,
            instance,
            targetRow;

        $(document).on('click', '.unpause-instance', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the instance-name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            instance = document.getElementById(id + "-name-text");

            // Add instance-name-text to delete-confirm-form
            $('div#instance-unpause-confirm-form > p > span.instance-name').empty().append($(instance).text());

            $("#instance-unpause-confirm-form").dialog("open");
        });

        $("#instance-unpause-confirm-form").dialog({
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
                    var confId = id,
                        confInstance = $(instance).text(),
                        confConsoleHtml = consoleLinks.items[confId].html;

                    message.showMessage('notice', "Unpausing " + confInstance + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("unpause-instance", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/unpause_server/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var statusCell = document.getElementById(confId + "-status-cell");

                                // Update status cell
                                $(statusCell).fadeOut().empty();
                                $(statusCell).append("ACTIVE").fadeIn();

                                // Create new actions
                                var newActions =
                                    confConsoleHtml +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="pause-instance ' + confId + '-disable-action">pause</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="suspend-instance ' + confId + '-disable-action">suspend</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                                // Update actions-cell
                                $(actionsCell).fadeOut().empty();
                                $(actionsCell).append(newActions).fadeIn();

                                // Remove paused class
                                $(targetRow).removeClass("instance-paused");

                                // Update instance
                                instances.items[confId].status = "ACTIVE";
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar, enabled instance actions and widget view links
                            disableProgressbar(progressbar, "instances", true);
                            disableActions("unpause-instance", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Suspend ---

    $(function () {

        // Local Variables
        var id,
            instance,
            targetRow;

        $(document).on('click', '.suspend-instance', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the instance-name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            instance = document.getElementById(id + "-name-text");

            // Add instance-name-text to confirm-form
            $('div#instance-suspend-confirm-form > p > span.instance-name').empty().append($(instance).text());

            $("#instance-suspend-confirm-form").dialog("open");
        });

        $("#instance-suspend-confirm-form").dialog({
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
                    var confId = id,
                        confInstance = $(instance).text();

                    message.showMessage('notice', "Suspending " + confInstance + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("suspend-instance", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/suspend_server/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var statusCell = document.getElementById(confId + "-status-cell");

                                // Update status cell
                                $(statusCell).fadeOut().empty();
                                $(statusCell).append("SUSPENDED").fadeIn();

                                // Create new actions
                                var newActions =
                                    '<a href="#" class="resume-instance ' + confId + '-disable-action">resume</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                                // Update actions-cell
                                $(actionsCell).fadeOut().empty();
                                $(actionsCell).append(newActions).fadeIn();

                                // Add paused class
                                $(targetRow).addClass("instance-suspended");

                                // Update instance
                                instances.items[confId].status = "SUSPENDED";
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar, enabled instance actions and widget view links
                            disableProgressbar(progressbar, "instances", true);
                            disableActions("suspend-instance", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Resume ---

    $(function () {

        // Local Variables
        var id,
            instance,
            targetRow;

        $(document).on('click', '.resume-instance', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the instance-name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            instance = document.getElementById(id + "-name-text");

            // Add instance-name-text to confirm-form
            $('div#instance-resume-confirm-form > p > span.instance-name').empty().append($(instance).text());

            $("#instance-resume-confirm-form").dialog("open");
        });

        $("#instance-resume-confirm-form").dialog({
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
                    var confId = id,
                        confInstance = $(instance).text(),
                        confConsoleHtml = consoleLinks.items[confId].html;

                    message.showMessage('notice', "Resuming " + confInstance + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and instance actions
                    disableLinks(true);
                    disableActions("resume-instance", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "instances", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/resume_server/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var statusCell = document.getElementById(confId + "-status-cell");

                                // Update status cell
                                $(statusCell).fadeOut().empty();
                                $(statusCell).append("ACTIVE").fadeIn();

                                // Create new actions
                                var newActions =
                                    confConsoleHtml +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="pause-instance ' + confId + '-disable-action">pause</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="suspend-instance ' + confId + '-disable-action">suspend</a>' +
                                    '<span class="instance-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-instance ' + confId + '-disable-action">delete</a>';

                                // Update actions-cell
                                $(actionsCell).fadeOut().empty();
                                $(actionsCell).append(newActions).fadeIn();

                                // Remove paused class
                                $(targetRow).removeClass("instance-suspended");

                                // Update instance
                                instances.items[confId].status = "ACTIVE";
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar, enabled instance actions and widget view links
                            disableProgressbar(progressbar, "instances", true);
                            disableActions("resume-instance", false);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });
});