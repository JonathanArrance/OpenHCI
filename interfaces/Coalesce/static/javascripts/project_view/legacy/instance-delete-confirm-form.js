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

    // Local Variables
    var id,
        instance,
        targetRow;

    // Widget Elements
    var progressbar = $("#instance_progressbar"),
        table = $("#instance_list"),
        placeholder =
            '<tr id="instance_placeholder"><td><p><i>This project has no instances</i></p></td><td></td><td></td><td></td></tr>';

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
                                    '<span class="volume-actions-pipe"> | </span>' +
                                    '<a href="#" class="delete-volume">delete</a>';
                                $(volActionsCell).append(newVolAction).fadeIn();
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
                            }

                            // Remove from instances
                            instances.removeItem(confId);
                            instanceOpts.removeItem(confId);

                            // If last row, append placeholder
                            var rowCount = $('#instance_list tr').length;
                            if (rowCount < 2) {
                                $(table).append(placeholder).fadeIn();
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
});
