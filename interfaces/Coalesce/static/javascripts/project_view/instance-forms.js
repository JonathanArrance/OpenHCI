// Declare click events after document has loaded
$(function () {

    // --- Create ---

    $("#create-instance").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Create Form
        var form = $("<div></div>")
            .prop("id", "instance-dialog-form")
            .prop("title", "Create Instance")
            .css("display", "none")
            .append($("<p></p>")
                .prop("class", "validateTips")
                .html("Create a new instance. All form fields are required."))
            .append($("<form></form>")
                .append($("<fieldset></fieldset>")
                    .append($("<label></label>")
                        .prop("for", "name")
                        .html("Instance Name"))
                    .append($("<input></input>")
                        .prop("id", "name")
                        .prop("name", "name")
                        .prop("type", "text"))
                    .append($("<label></label>")
                        .prop("for", "group")
                        .html("Security Group"))
                    .append($("<select></select>")
                        .prop("id", "group")
                        .prop("name", "group"))
                    .append($("<label></label>")
                        .prop("for", "key")
                        .html("Security Key"))
                    .append($("<select></select>")
                        .prop("id", "key")
                        .prop("name", "key"))
                    .append($("<label></label>")
                        .prop("for", "network")
                        .html("Private Network"))
                    .append($("<select></select>")
                        .prop("id", "network")
                        .prop("name", "network"))
                    .append($("<label></label>")
                        .prop("for", "image")
                        .html("Image"))
                    .append($("<select></select>")
                        .prop("id", "image")
                        .prop("name", "image"))
                    .append($("<label></label>")
                        .prop("for", "flavor")
                        .html("Flavor"))
                    .append($("<select></select>")
                        .prop("id", "flavor")
                        .prop("name", "flavor"))));

        // Populate selects
        refreshSelect(form.find("#group"), secGroupInstOpts);
        refreshSelect(form.find("#key"), secKeyInstOpts);
        refreshSelect(form.find("#network"), privNetInstOpts);
        refreshSelect(form.find("#image"), imageInstOpts);
        refreshSelect(form.find("#flavor"), flavors);

        // Open dialog form
        form.dialog({
            autoOpen: true,
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
                    // Create Instance
                    createInstance($("#name"), $("#group"), $("#key"), $("#network"), $("#image"), $("#flavor"));
                }
            },
            close: function () {

                // Reset form validation
                resetUiValidation([$("#name"), $("#group"), $("#key"), $("#network"), $("#image"), $("#flavor")]);

                // Remove dialog form
                $(this).remove();
            }
        });
    });

    // --- Delete ---

    $(document).on('click', '.delete-instance', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));

        // Create form
        $("<div></div>")
            .prop("id", "instance-delete-confirm-form")
            .prop("title", "Delete Instance")
            .css("display", "none")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Delete " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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

                        // Delete instance
                        deleteInstance(id, instance, targetRow);

                        // Close Dialog form
                        $(this).remove();
                    }
                }
            });
    });

    // --- Pause ---

    $(document).on('click', '.pause-instance', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));

        // Create form
        $("<div></div>")
            .prop("id", "instance-pause-confirm-form")
            .prop("title", "Pause Instance")
            .css("display", "none")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Pause " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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

                        // Pause instance
                        pauseInstance(id, instance, targetRow);

                        // Close Dialog form
                        $(this).remove();
                    }
                }
            });
    });

    // --- Unpause ---

    $(document).on('click', '.unpause-instance', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));

        // Add instance-name-text to delete-confirm-form
        $('div#instance-unpause-confirm-form > p > span.instance-name').empty().append(instance.text());

        // Create form
        $("<div></div>")
            .prop("id", "instance-unpause-confirm-form")
            .prop("title", "Unpause Instance")
            .css("display", "none")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Unpause " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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

                        // Unpause Instance
                        unpauseInstance(id, instance, targetRow);

                        // Close dialog form
                        $(this).remove();
                    }
                }
            });
    });

    // --- Suspend ---

    $(document).on('click', '.suspend-instance', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));

        // Create form
        $("<div></div>")
            .prop("id", "instance-suspend-confirm-form")
            .prop("title", "Suspend Instance")
            .css("display", "none")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Suspend " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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

                        // Suspend instance
                        suspendInstance(id, instance, targetRow);

                        // Close dialog form
                        $(this).remove();
                    }
                }
            });
    });
});

// --- Resume ---

$(document).on('click', '.resume-instance', function (event) {

    // Prevent scrolling to top of page on click
    event.preventDefault();

    // Get target row element, get id from that element and use that to get the instance-name-text
    var targetRow = $(this).parent().parent(),
        id = $(targetRow).attr("id"),
        instance = $(document.getElementById(id + "-name-text"));

    // Create form
    $("<div></div>")
        .prop("id", "instance-resume-confirm-form")
        .prop("title", "Resume Instance")
        .css("display", "none")
        .append($("<p></p>")
            .css("text-align", "center")
            .html("Resume " + instance.text() + "?"))
        .dialog({
            autoOpen: true,
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

                    // Resume instance
                    resumeInstance(id, instance, targetRow);

                    // Close dialog form
                    $(this).remove();
                }
            }
        });
});

function createInstance(name, secGroup, secKey, network, image, flavor) {

    // Gather inputs
    var allFields = $([]).add(name).add(secGroup).add(secKey).add(network).add(image).add(flavor);

    // Remove UI validation flags
    clearUiValidation(allFields);

    // Validate form inputs
    var isValid =
        checkLength(name, "Instance Name", 3, 16) &&
        checkDuplicateName(name, instanceOpts);

    // If Valid, create instance
    if (isValid) {

        // Remove dialog form
        $("#instance-dialog-form").remove();

        // Confirmed Selections
        var confName = name.val(),
            confSecGroup = secGroup.val(),
            confSecKey = secKey.val(),
            confNetwork = network.val(),
            confImage = image.val(),
            confFlavor = flavor.val();

        // Show toast message
        message.showMessage('notice', 'Creating New Instance ' + confName);

        // Hide widget buttons and disable widget view links
        setVisible('#create-instance', false);
        disableLinks(true);

        // Initialize progressbar and make it visible if hidden
        $("#instance_progressbar").progressbar({value: false});
        disableProgressbar($("#instance_progressbar"), "instances", false);

        // Make AJAX call and handle response
        $.getJSON('/create_image/' + confName + '/' + confSecGroup + '/nova/' + confFlavor + '/' + confSecKey + '/' + confImage + '/' + confNetwork + '/' + PROJECT_ID + '/')
            .done(function (data) {

                if (data.status == 'error') {

                    // Show toast message
                    message.showMessage('error', data.message);
                }

                if (data.status == 'success') {

                    // Show toast message
                    message.showMessage('success', data.message);

                    // Add new row
                    addInstance(data);
                }
            })
            .fail(function () {

                // Show toast message
                message.showMessage('error', 'Server Fault');
            })
            .always(function () {

                // Reset interface
                checkAssignFip();
                disableProgressbar($("#instance_progressbar"), "instances", true);
                setVisible('#create-instance', true);
                disableLinks(false);
                resetUiValidation(allFields);
            });
    }
}

function addInstance(data) {

    // Create new row element and append it to instance_list
    $("<tr></tr>")
        .prop("id", data.server_info.server_id)
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-name-cell')
            .append($("<a></a>")
                .prop("href", '/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/')
                .append($("<span></span>")
                    .prop("id", data.server_info.server_id + '-name-text')
                    .html(data.server_info.server_name.toString()))))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-status-cell')
            .html("ACTIVE"))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-os-cell')
            .html(data.server_info.server_os.toString() + ' / ' + data.server_info.server_flavor.toString()))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-actions-cell')
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", "open-instance-console")
                .on("click", function () {
                    window.open(
                        data.server_info.novnc_console,
                        "_blank",
                        "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                })
                .html("console"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'pause-instance ' + data.server_info.server_id + '-disable-action')
                .html("pause"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'suspend-instance ' + data.server_info.server_id + '-disable-action')
                .html("suspend"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'delete-instance ' + data.server_info.server_id + '-disable-action')
                .html("delete")))
        .appendTo($("#instance_list"))
        .fadeIn();

    // Check table length, remove placeholder if necessary
    if ($('#instance_list tr').length >= 2) {
        $('#instance_placeholder').remove().fadeOut();
        setVisible("#create-instance-snapshot", true);
    }

    // Add to instances and consoleLinks
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

    // Add to selects
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance"), attachableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#assign_instance"), assignableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance_to_snap"), instanceOpts);
}

function deleteInstance(id, name, row) {

    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;

    // Show toast message
    message.showMessage('notice', "Deleting " + confInstance + ".");

    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = $(actionsCell.innerHTML);

    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("delete-instance", true);

    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);

    // Clear clicked action link and replace with loader
    actionsCell
        .empty()
        .append($("<div></div>")
            .prop("id", confId + '-loader')
            .prop("class", "ajax-loader")
            .fadeIn());

    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/delete_server/')
        .done(function (data) {

            if (data.status == 'error') {

                // Show toast message
                message.showMessage('error', data.message);

                // Restore actions cell html
                actionsCell
                    .empty()
                    .append(actionsHtml
                        .fadeIn());
            }

            if (data.status == 'success') {

                // Show toast message
                message.showMessage('success', data.message);

                // Remove row
                confRow.fadeOut().remove();

                // Update selects
                removeFromSelect(confId, $("#instance"), attachableInstances);
                removeFromSelect(confId, $("#assign_instance"), assignableInstances);

                // If last assignable instance, or no available ips, hide "Assign" IP button
                if (assignableFips.length <= 0 || assignableInstances.length <= 0) {
                    setVisible('#assign_ip', false);
                }

                // Unattach volumes
                for (var i = 0; i < data.vols.length; i++) {

                    $(document.getElementById(data.vols[i] + '-attached-cell'))
                        .empty()
                        .fadeOut()
                        .append($("<span></span>")
                            .prop("id", data.vols[i] + '-attached-placeholder')
                            .html("No Attached Instance")
                            .fadeIn())
                        .parent()
                        .removeClass("volume-attached");

                    $(document.getElementById(data.vols[i] + '-actions-cell'))
                        .empty()
                        .fadeOut()
                        .append($("<a></a>")
                            .prop("href", "#")
                            .prop("class", "attach-volume")
                            .html("attach"))
                        .append($("<span></span>")
                            .prop("class", "volume-actions-pipe")
                            .html(" | "))
                        .append($("<a></a>")
                            .prop("href", "#")
                            .prop("class", "clone-volume")
                            .html("clone"))
                        .append($("<span></span>")
                            .prop("class", "volume-actions-pipe")
                            .html(" | "))
                        .append($("<a></a>")
                            .prop("href", "#")
                            .prop("class", "revert-volume")
                            .html("revert"))
                        .append($("<span></span>")
                            .prop("class", "volume-actions-pipe")
                            .html(" | "))
                        .append($("<a></a>")
                            .prop("href", "#")
                            .prop("class", "delete-volume")
                            .html("delete"))
                        .fadeIn();

                    snapshotVolumes.setItem(data.vols[i], {
                        value: data.vols[i],
                        option: volumes.items[data.vols[i]].name
                    })
                }

                // Unassign floating IPs
                for (var j = 0; j < data.floating_ip.length; j++) {

                    $(document.getElementById(data.floating_ip_id[j] + '-instance-cell'))
                        .empty()
                        .fadeOut()
                        .append($("<span></span>")
                            .prop("id", data.floating_ip[j] + '-instance-name')
                            .html("None"))
                        .parent()
                        .removeClass("fip-assigned")
                        .fadeIn();

                    $(document.getElementById(data.floating_ip_id[j] + '-actions-cell'))
                        .empty()
                        .fadeOut()
                        .append($("<a></a>")
                            .prop("id", data.floating_ip_id[j])
                            .prop("class", "deallocate-ip")
                            .prop("href", "#")
                            .html("deallocate"))
                        .fadeIn();

                    assignableFips.setItem(data.floating_ip_id[j], {
                        value: data.floating_ip_id[j],
                        option: fips.getItem(data.floating_ip_id[j]).ip
                    })
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
                if ($('#instance_list tr').length < 2) {
                    $("<tr></tr>")
                        .prop("id", "instance_placeholder")
                        .append($("<td></td>")
                            .append($("<p></p>")
                                .append($("<i></i>")
                                    .html("This project has no instances"))))
                        .append($("<td></td>"))
                        .append($("<td></td>"))
                        .appendTo($("#instance_list"))
                        .fadeIn();
                    setVisible("#create-instance-snapshot", false);
                }
            }
        })
        .fail(function () {

            message.showMessage('error', 'Server Fault');

            // Restore actions cell html
            actionsCell
                .empty()
                .append(actionsHtml
                    .fadeIn());
        })
        .always(function () {

            // Hide progressbar and enable widget view links
            checkAssignFip();
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("delete-instance", false);
            disableLinks(false);
        });
}

function pauseInstance(id, name, row) {

    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;

    // Show toast message
    message.showMessage('notice', "Pausing " + confInstance + ".");

    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = $(actionsCell.innerHTML);

    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("pause-instance", true);

    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);

    // Clear clicked action link and replace with loader
    actionsCell
        .empty()
        .append($("<div></div>")
            .prop("id", confId + '-loader')
            .prop("class", "ajax-loader")
            .fadeIn());

    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/pause_server/')
        .done(function (data) {

            if (data.status == 'error') {

                // Show toast message
                message.showMessage('error', data.message);

                // Restore actions cell html
                actionsCell
                    .empty()
                    .append(actionsHtml
                        .fadeIn());
            }

            if (data.status == 'success') {

                // Show toast message
                message.showMessage('success', data.message);

                var statusCell = $(document.getElementById(confId + "-status-cell"));

                // Update status cell
                statusCell
                    .empty()
                    .fadeOut()
                    .append("PAUSED")
                    .fadeIn();

                // Update actions-cell
                actionsCell
                    .empty()
                    .fadeOut()
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "unpause-instance")
                        .prop("href", "#")
                        .html("unpause"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "delete-instance")
                        .prop("href", "#")
                        .html("delete"))
                    .fadeIn();

                // Add paused class
                confRow.addClass("instance-paused");

                // Update instance
                instances.items[confId].status = "PAUSED";
            }
        })
        .fail(function () {

            // Show toast message
            message.showMessage('error', 'Server Fault');

            // Restore actions cell html
            actionsCell
                .empty()
                .append(actionsHtml
                    .fadeIn());
        })
        .always(function () {

            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("pause-instance", false);
            disableLinks(false);
        });
}

function unpauseInstance(id, name, row) {

    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;

    // Show toast message
    message.showMessage('notice', "Unpausing " + confInstance + ".");

    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = $(actionsCell.innerHTML);

    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("unpause-instance", true);

    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);

    // Clear clicked action link and replace with loader
    actionsCell
        .empty()
        .append($("<div></div>")
            .prop("id", confId + '-loader')
            .prop("class", "ajax-loader")
            .fadeIn());

    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/unpause_server/')
        .done(function (data) {

            if (data.status == 'error') {

                // Show toast message
                message.showMessage('error', data.message);

                // Restore actions cell html
                actionsCell
                    .empty()
                    .append(actionsHtml
                        .fadeIn());
            }

            if (data.status == 'success') {

                // Show toast message
                message.showMessage('success', data.message);

                var statusCell = $(document.getElementById(confId + "-status-cell"));

                // Update status cell
                statusCell
                    .empty()
                    .fadeOut()
                    .append("ACTIVE")
                    .fadeIn();

                // Update actions-cell
                actionsCell
                    .empty()
                    .fadeOut()
                    .append($("<a></a>")
                        .prop("href", "#")
                        .prop("class", "open-instance-console")
                        .on("click", function () {
                            window.open(consoleLinks.items[id].link, "_blank", "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                        })
                        .html("console"))
                    .append($("<span></span>")
                        .prop("class", "instance-actions-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "pause-instance")
                        .prop("href", "#")
                        .html("pause"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "suspend-instance")
                        .prop("href", "#")
                        .html("suspend"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "delete-instance")
                        .prop("href", "#")
                        .html("delete"))
                    .fadeIn();

                // Remove paused class
                confRow.removeClass("instance-paused");

                // Update instance
                instances.items[confId].status = "ACTIVE";
            }
        })
        .fail(function () {

            // Show toast message
            message.showMessage('error', 'Server Fault');

            // Restore Actions html
            actionsCell
                .empty()
                .fadeOut()
                .append(actionsHtml)
                .fadeIn();
        })
        .always(function () {

            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("unpause-instance", false);
            disableLinks(false);
        });
}

function suspendInstance(id, name, row) {

    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;

    // Show toast message
    message.showMessage('notice', "Suspending " + confInstance + ".");

    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = $(actionsCell.innerHTML);

    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("suspend-instance", true);

    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);

    // Clear clicked action link and replace with loader
    actionsCell
        .empty()
        .append($("<div></div>")
            .prop("id", confId + '-loader')
            .prop("class", "ajax-loader")
            .fadeIn());

    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/suspend_server/')
        .done(function (data) {

            if (data.status == 'error') {

                // Show toast message
                message.showMessage('error', data.message);

                // Restore actions cell html
                actionsCell
                    .empty()
                    .append(actionsHtml
                        .fadeIn());
            }

            if (data.status == 'success') {

                // Show toast message
                message.showMessage('success', data.message);

                var statusCell = $(document.getElementById(confId + "-status-cell"));

                // Update status cell
                statusCell
                    .empty()
                    .fadeOut()
                    .append("SUSPENDED")
                    .fadeIn();

                // Update actions-cell
                actionsCell
                    .empty()
                    .fadeOut()
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "resume-instance")
                        .prop("href", "#")
                        .html("resume"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "delete-instance")
                        .prop("href", "#")
                        .html("delete"))
                    .fadeIn();

                // Add paused class
                confRow.addClass("instance-suspended");

                // Update instance
                instances.items[confId].status = "SUSPENDED";
            }
        })
        .fail(function () {

            // Show toast message
            message.showMessage('error', 'Server Fault');

            // Restore Actions html
            actionsCell
                .empty()
                .fadeOut()
                .append(actionsHtml)
                .fadeIn();
        })
        .always(function () {

            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("suspend-instance", false);
            disableLinks(false);
        });
}

function resumeInstance(id, name, row) {

    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;

    // Show toast message
    message.showMessage('notice', "Resuming " + confInstance + ".");

    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = $(actionsCell.innerHTML);

    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("resume-instance", true);

    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);

    // Clear clicked action link and replace with loader
    actionsCell
        .empty()
        .append($("<div></div>")
            .prop("id", confId + '-loader')
            .prop("class", "ajax-loader")
            .fadeIn());

    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/resume_server/')
        .done(function (data) {

            if (data.status == 'error') {

                // Show toast message
                message.showMessage('error', data.message);

                // Restore actions cell html
                actionsCell
                    .empty()
                    .append(actionsHtml
                        .fadeIn());
            }

            if (data.status == 'success') {

                // Show toast message
                message.showMessage('success', data.message);

                var statusCell = $(document.getElementById(confId + "-status-cell"));

                // Update status cell
                statusCell
                    .empty()
                    .fadeOut()
                    .append("ACTIVE")
                    .fadeIn();

                // Update actions-cell
                actionsCell
                    .empty()
                    .fadeOut()
                    .append($("<a></a>")
                        .prop("href", "#")
                        .prop("class", "open-instance-console")
                        .on("click", function () {
                            window.open(consoleLinks.items[id].link, "_blank", "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                        })
                        .html("console"))
                    .append($("<span></span>")
                        .prop("class", "instance-actions-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "pause-instance")
                        .prop("href", "#")
                        .html("pause"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "suspend-instance")
                        .prop("href", "#")
                        .html("suspend"))
                    .append($("<span></span>")
                        .prop("class", "instance-action-pipe")
                        .html(" | "))
                    .append($("<a></a>")
                        .prop("id", confId + '-disable-action')
                        .prop("class", "delete-instance")
                        .prop("href", "#")
                        .html("delete"))
                    .fadeIn();

                // Remove paused class
                confRow.removeClass("instance-suspended");

                // Update instance
                instances.items[confId].status = "ACTIVE";
            }
        })
        .fail(function () {

            // Show toast message
            message.showMessage('error', 'Server Fault');

            // Restore Actions html
            actionsCell
                .empty()
                .fadeOut()
                .append(actionsHtml)
                .fadeIn();
        })
        .always(function () {

            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("resume-instance", false);
            disableLinks(false);
        });
}
