$(function () {

    var csrftoken = getCookie('csrftoken');
    var instanceId = '';    // Initialize empty string to hold ID of clicked instance

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-pause-confirm-form").dialog({
        autoOpen: false,
        height: 150,
        width: 250,
        modal: true,
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Pausing Instance');

                var confirmedId = instanceId;   // Initialize string to hold ID of confirmed instance
                var pauseHtml = '<a href="#" class="pause-instance '+confirmedId+'-disable-action">pause</a>';
                var unpauseHtml = '<a href="#" class="unpause-instance">unpause</a>';

                // Create loader
                var pauseAction = '#' + confirmedId + '-actions-cell > .pause-instance';
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(pauseAction).empty().fadeOut();
                $(pauseAction).append(loaderHtml).fadeIn();

                disableActions(confirmedId, true);
                disableLinks(true);

                $.getJSON('/server/' + PROJECT_ID + '/' + confirmedId + '/pause_server/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Recall clicked action link on error
                            $(pauseAction).empty().fadeOut();
                            $(pauseAction).append(pauseHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var statusCell = '#' + confirmedId + '-status-cell';
                            var actionsCell = '#' + confirmedId + '-actions-cell';

                            // Update status and actions cells
                            $(statusCell).fadeOut().empty();
                            $(actionsCell).fadeOut().empty();
                            $(statusCell).append("PAUSED").fadeIn();
                            $(actionsCell).append(unpauseHtml).fadeIn();

                            disableActions(confirmedId, false);
                            disableLinks(false);
                        }
                    })
                    .error(function () {

                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
                        $(pauseAction).empty().fadeOut();
                        $(pauseAction).append(pauseHtml).fadeIn();

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

    $(document).on('click', '.pause-instance', function () {

        instanceId = $(this).parent().parent().attr('id');

        // Clear and add instance name to .instance-name span in confirm statement
        var nameSelector = '#' + instanceId + '-name-text';
        $('#instance-pause-confirm-form > p > span.instance-name').empty().append($(nameSelector).text());

        $("#instance-pause-confirm-form").dialog("open");
    });
});