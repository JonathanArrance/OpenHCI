$(function () {

    var csrftoken = getCookie('csrftoken');
    var instanceId = '';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-unpause-confirm-form").dialog({
        autoOpen: false,
        height: 150,
        width: 250,
        modal: true,
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Unpausing Instance');
                var confirmedId = instanceId;
                var unpauseHtml = '<a href="#" class="unpause-instance '+confirmedId+'-disable-action">unpause</a>';
                var activeActions = '';    // New actions html string
                    activeActions += '<a href="{{v.novnc_console}}" target="_blank">console</a>';
                    activeActions += '<span class="instance-actions-pipe"> | </span>';
                    activeActions += '<a href="#" class="pause-instance '+confirmedId+'-disable-action">pause</a>';
                    activeActions += '<span class="instance-actions-pipe"> | </span>';
                    activeActions += '<a href="#" class="suspend-instance '+confirmedId+'-disable-action">suspend</a>';

                // Create loader
                var unpauseAction = '#' + confirmedId + '-actions-cell > .unpause-instance';
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(unpauseAction).empty().fadeOut();
                $(unpauseAction).append(loaderHtml).fadeIn();

                disableActions(confirmedId, true);
                disableLinks(true);

                $.getJSON('/server/' + PROJECT_ID + '/' + confirmedId + '/unpause_server/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Recall clicked action link on error
                            $(unpauseAction).empty().fadeOut();
                            $(unpauseAction).append(unpauseHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var statusCell = '#' + confirmedId + '-status-cell';
                            var actionsCell = '#' + confirmedId + '-actions-cell';

                            // Update status and actions cells
                            $(statusCell).fadeOut().empty();
                            $(actionsCell).fadeOut().empty();
                            $(statusCell).append("ACTIVE").fadeIn();
                            $(actionsCell).append(activeActions).fadeIn();
                        }

                        disableActions(confirmedId, false);
                        disableLinks(false);
                    })
                    .error(function () {
                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
                        $(unpauseAction).empty().fadeOut();
                        $(unpauseAction).append(unpauseHtml).fadeIn();

                        disableActions(confirmedId, false);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        }
    })

    $(document).on('click', '.unpause-instance', function () {

        instanceId = $(this).parent().parent().attr('id');

        // Clear and add instance name to .instance-name span in confirm statement
        var nameSelector = '#' + instanceId + '-name-text';
        $('#instance-unpause-confirm-form > p > span.instance-name').empty().append($(nameSelector).text());

        $("#instance-unpause-confirm-form").dialog("open");
    });
});
