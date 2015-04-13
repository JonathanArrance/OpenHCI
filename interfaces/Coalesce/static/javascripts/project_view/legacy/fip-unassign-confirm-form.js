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
    var targetRow,
        fip,
        fipId,
        instanceName,
        instanceId;

    // Widget Elements
    var progressbar = $("#fip_progressbar");

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
                            var newActions = '<a href="#" class="deallocate_ip">deallocate</a>';

                            $(instanceCell).empty().fadeOut();
                            $(actionsCell).empty().fadeOut();

                            $(instanceCell).append(instanceNameHtml).fadeIn();
                            $(actionsCell).append(newActions).fadeIn();

                            // Update assign_ip selects
                            addToSelect(data.floating_ip_id, data.floating_ip, $("#assign_floating_ip"), assignableFips);
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
                        disableActions("unassign_ip", false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },

        close: function () {
        }
    });

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
});