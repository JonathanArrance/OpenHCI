$(function () {

    // Widget Elements
    var progressbar = $("#fip_progressbar"),
        table = $("#fip_list"),
        placeholder =
            '<tr id="fip_placeholder"><td><p><i>This project has no floating IPs</i></p></td><td></td><td></td></tr>';

    // --- Allocate ---

    $("#allocate_ip").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        message.showMessage('notice', "Allocating IP.");

        // Disable links and widget buttons
        disableLinks(true);
        setVisible('#allocate_ip', false);
        setVisibleInLineBlock('#allocate_ip', false);
        setVisible('#assign_ip', false);
        setVisibleInLineBlock('#assign_ip', false);

        // Initialize progressbar and make it visible if hidden
        $(progressbar).progressbar({value: false});
        disableProgressbar(progressbar, "fips", false);

        $.getJSON('/allocate_floating_ip/' + PROJECT_ID + '/' + extNet + '/')
            .done(function (data) {

                if (data.status == 'error') {

                    message.showMessage('error', "No available IPs.  If you just deallocated an IP, wait a few minutes and try again.");
                }

                if (data.status == 'success') {

                    message.showMessage('success', "Successfully allocated " + data.ip_info.floating_ip + ".");

                    // Generate new row html
                    var newRow =
                        '<tr id="' + data.ip_info.floating_ip_id + '">' +
                        '<td id="' + data.ip_info.floating_ip_id + '-ip-cell">' +
                        '<a href="/floating_ip/' + data.ip_info.floating_ip_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                        '<span id="' + data.ip_info.floating_ip_id + '-ip-address">' + data.ip_info.floating_ip + '</span></a></td>' +
                        '<td id="' + data.ip_info.floating_ip_id + '-instance-cell"><span id="' + data.ip_info.floating_ip_id + '-instance-name">None</span></td>' +
                        '<td id="' + data.ip_info.floating_ip_id + '-actions-cell"><a href="#" " class="deallocate-ip">deallocate</a></td>' +
                        '</tr>';

                    // If first fip, remove placeholder
                    var rowCount = $('#fip_list tr').length;
                    if (rowCount <= 2) {
                        $('#fip_placeholder').remove().fadeOut();
                    }

                    // Append new row
                    $(table).append(newRow).fadeIn();

                    fips.setItem(data.ip_info.floating_ip_id, {
                        id: data.ip_info.floating_ip_id,
                        ip: data.ip_info.floating_ip
                    });

                    // Add option to assign_ip select
                    addToSelect(data.ip_info.floating_ip_id, data.ip_info.floating_ip, $("#assign_floating_ip"), assignableFips);
                    refreshSelect($("#bam-security-ip"), assignableFips);
                    $('<option></option>')
                        .val("none")
                        .html("Skip Attaching IP")
                        .prop("selected", "selected")
                        .prependTo($("#bam-security-ip"));
                }
            })
            .fail(function () {

                message.showMessage('error', 'Server Fault');
            })
            .always(function () {

                // Reset interface
                checkAssignFip();
                disableProgressbar(progressbar, "fips", true);
                setVisible('#allocate_ip', true);
                setVisibleInLineBlock('#allocate_ip', true);
                disableLinks(false);
            });
    });

    // --- Deallocate ---

    $(function () {

        // Local Variables
        var id,
            fip,
            targetRow;

        $(document).on('click', '.deallocate-ip', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get form text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            fip = $(document.getElementById(id + "-ip-address")).text();

            // Add ip to form
            $('div#fip-deallocate-confirm-form > p > span.ip-address').empty().append(fip);
            $('#fip-deallocate-confirm-form').dialog("open");
        });

        $('#fip-deallocate-confirm-form').dialog({
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
                    var
                        confId = id,
                        confFip = fip,
                        confRow = targetRow;

                    message.showMessage('notice', "Deallocating " + confFip + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = '<a class="deallocate-ip" href="#">deallocate</a></td>';

                    // Disable widget view links, disable deallocate actions and hide allocate and assign buttons
                    disableLinks(true);
                    disableActions("deallocate-ip", true);
                    setVisible('#allocate_ip', false);
                    setVisibleInLineBlock('#allocate_ip', false);
                    setVisible('#assign_ip', false);
                    setVisibleInLineBlock('#assign_ip', false);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "fips", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/deallocate_floating_ip/' + PROJECT_ID + '/' + confFip + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Reset actions cell
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Remove row
                                $(confRow).fadeOut().remove();

                                // If last fip, reveal placeholder and hide assign_ip
                                var rowCount = $('#fip_list tr').length;
                                if (rowCount < 2) {
                                    $(table).append(placeholder).fadeIn();
                                }

                                fips.removeItem(confId);

                                // Remove ip from assign_ip select
                                removeFromSelect(confId, $("#assign_floating_ip"), assignableFips);
                                refreshSelect($("#bam-security-ip"), assignableFips);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Attaching IP")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-security-ip"));
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            checkAssignFip();
                            disableProgressbar(progressbar, "fips", true);
                            setVisible('#allocate_ip', true);
                            setVisibleInLineBlock('#allocate_ip', true);
                            setVisible('#assign_ip', true);
                            setVisibleInLineBlock('#assign_ip', true);
                            disableLinks(false);
                            disableActions("deallocate-ip", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Assign ---

    $(function () {

        // Form Elements
        var floating_ip = $("#assign_floating_ip"),
            instance = $("#assign_instance");

        $("#assign_ip").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#fip-assign-dialog-form").dialog("open");
        });

        $("#fip-assign-dialog-form").dialog({
            autoOpen: false,
            height: 265,
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
                "Assign": function () {

                    // Confirmed Selections
                    var confIpId = floating_ip.val(),
                        confIp = $(document.getElementById(confIpId + "-ip-address")).text(),
                        confInstanceId = instance.val(),
                        targetRow = document.getElementById(confIpId);

                    // Disable widget view links and hide widget buttons
                    disableLinks(true);
                    setVisible('#allocate_ip', false);
                    setVisibleInLineBlock('#allocate_ip', false);
                    setVisible('#assign_ip', false);
                    setVisibleInLineBlock('#assign_ip', false);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "fips", false);

                    $.getJSON('/assign_floating_ip/' + confIp + '/' + confInstanceId + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Update instance and action cells
                                var instanceCell = document.getElementById(data.floating_ip_id + "-instance-cell");
                                var actionsCell = document.getElementById(data.floating_ip_id + "-actions-cell");
                                var instanceHtml = '<span id="' + data.floating_ip_id + '-instance-name">' + data.instance_name + '</span>';
                                var newAction = '<a href="#" id="' + data.floating_ip_id + '" class="unassign_ip">unassign</a>';

                                $(instanceCell).empty().fadeOut();
                                $(actionsCell).empty().fadeOut();

                                $(instanceCell).append(instanceHtml).fadeIn();
                                $(actionsCell).append(newAction).fadeIn();

                                // Update assign_ip selects
                                removeFromSelect(data.floating_ip_id, floating_ip, assignableFips);
                                refreshSelect($("#bam-security-ip"), assignableFips);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Attaching IP")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-security-ip"));
                                removeFromSelect(confInstanceId, instance, assignableInstances);

                                // Add assigned class
                                $(targetRow).addClass("fip-assigned");
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            // Reset interface
                            checkAssignFip();
                            disableProgressbar(progressbar, "fips", true);
                            setVisible('#allocate_ip', true);
                            setVisibleInLineBlock('#allocate_ip', true);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });

    // --- Unassign ---

    $(function () {

        // Local Variables
        var targetRow,
            fip,
            fipId,
            instanceName,
            instanceId;

        $(document).on('click', '.unassign_ip', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get form text
            targetRow = $(this).parent().parent();
            fipId = $(targetRow).attr("id");
            fip = $(document.getElementById(fipId + "-ip-address")).text();
            instanceName = $(document.getElementById(fipId + "-instance-name")).text();
            instanceId = $('a').filter(function () {
                return $(this).text() == instanceName;
            });
            instanceId = $(instanceId).parent().parent().attr("id");

            // Add ip to form
            $('div#fip-unassign-confirm-form > p > span.ip-address').empty().append(fip);
            $('#fip-unassign-confirm-form').dialog("open");
        });

        $("#fip-unassign-confirm-form").dialog({
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
                of: window
            },
            buttons: {
                "Confirm": function () {

                    // Confirmed Selections
                    var confFip = fip,
                        confFipId = fipId,
                        confInstanceId = instanceId,
                        confInstanceName = instanceName;

                    message.showMessage('notice', "Unassigning " + confFip + ".");

                    // Store action cell html
                    var actionsCell = document.getElementById(confFipId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and hide assign_ip button
                    disableLinks(true);
                    disableActions("unassign_ip", true);
                    setVisible('#assign_ip', false);
                    setVisibleInLineBlock('#assign_ip', false);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "fips", false);

                    // Create loader
                    var loaderId = confFipId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/unassign_floating_ip/' + confFipId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Reset actions cell
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Update instance and action cells
                                var instanceCell = document.getElementById(data.floating_ip_id + "-instance-cell");
                                var instanceNameHtml = '<span id="' + data.floating_ip_id + '-instance-name">None</span>';
                                var newActions = '<a href="#" class="deallocate-ip">deallocate</a>';

                                $(instanceCell).empty().fadeOut();
                                $(actionsCell).empty().fadeOut();

                                $(instanceCell).append(instanceNameHtml).fadeIn();
                                $(actionsCell).append(newActions).fadeIn();

                                // Update assign_ip selects
                                addToSelect(data.floating_ip_id, data.floating_ip, $("#assign_floating_ip"), assignableFips);
                                refreshSelect($("#bam-security-ip"), assignableFips);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Attaching IP")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-security-ip"));
                                addToSelect(confInstanceId, confInstanceName, $("#assign_instance"), assignableInstances);

                                // Remove assigned class
                                $(targetRow).removeClass("fip-assigned");
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Reset action cell
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml);
                        })
                        .always(function () {

                            // Reset interface
                            checkAssignFip();
                            disableProgressbar(progressbar, "fips", true);
                            setVisible('#assign_ip', true);
                            setVisibleInLineBlock('#assign_ip', true);
                            disableActions("unassign_ip", false);
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
