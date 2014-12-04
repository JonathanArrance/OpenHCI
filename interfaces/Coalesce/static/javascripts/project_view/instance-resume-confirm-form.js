$(function () {

    var csrftoken = getCookie('csrftoken');
    var instanceId = '';    // Initialize empty string to hold current instance ID

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-resume-confirm-form").dialog({
        autoOpen: false,
        height: 150,
        width: 250,
        modal: true,
        buttons: {
            "Confirm": function () {

                message.showMessage('notice', 'Resuming Instance');
                var confirmedId = instanceId;   // Initialize string to hold ID of confirmed instance
                var resumeHtml = '<a href="#" class="resume-instance '+confirmedId+'-disable-action">resume</a>';
                var activeActions = ''; // New actions html string
                    activeActions += '<a href="{{v.novnc_console}}" target="_blank">console</a>';
                    activeActions += '<span class="instance-actions-pipe"> | </span>';
                    activeActions += '<a href="#" class="pause-instance '+confirmedId+'-disable-action">pause</a>';
                    activeActions += '<span class="instance-actions-pipe"> | </span>';
                    activeActions += '<a href="#" class="suspend-instance '+confirmedId+'-disable-action">suspend</a>';

                // Create loader
                var resumeAction = '#' + confirmedId + '-actions-cell > .resume-instance';
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(resumeAction).empty().fadeOut();
                $(resumeAction).append(loaderHtml).fadeIn();

                disableActions(confirmedId, true);
                disableLinks(true);

                $.getJSON('/server/' + PROJECT_ID + '/' + confirmedId + '/resume_server/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Recall clicked action link on error
                            $(resumeAction).empty().fadeOut();
                            $(resumeAction).append(resumeHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var statusCell = '#' + confirmedId + '-status-cell';
                            var actionsCell = '#' + confirmedId + '-actions-cell';

                            // Update status and actions cells
                            $(statusCell).empty().fadeOut();
                            $(actionsCell).empty().fadeOut();
                            $(statusCell).append("ACTIVE").fadeIn();
                            $(actionsCell).append(activeActions).fadeIn();
                        }

                        disableActions(confirmedId, false);
                        disableLinks(false);
                    })
                    .error(function () {
                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
                        $(resumeAction).empty().fadeOut();
                        $(resumeAction).append(resumeHtml).fadeIn();

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

    $(document).on('click', '.resume-instance', function () {

        instanceId = $(this).parent().parent().attr('id');

        // Clear and add instance name to .instance-name span in confirm statement
        var nameSelector = '#' + instanceId + '-name-text';
        $('#instance-resume-confirm-form > p > span.instance-name').empty().append($(nameSelector).text());

        $("#instance-resume-confirm-form").dialog("open");
    });
});