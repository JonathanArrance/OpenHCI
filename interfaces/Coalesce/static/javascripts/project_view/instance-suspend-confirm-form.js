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

    $("#instance-suspend-confirm-form").dialog({
        autoOpen: false,
        height: 150,
        width: 250,
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

                message.showMessage('notice', 'Suspending Instance');
                var confirmedId = instanceId;
                var suspendHtml = '<a href="#" class="suspend-instance '+confirmedId+'-disable-action">suspend</a>';
                var resumeHtml = '<a href="#" class="resume-instance '+confirmedId+'-disable-action">resume</a>';

                // Create loader
                var suspendAction = '#' + confirmedId + '-actions-cell > .suspend-instance';
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(suspendAction).empty().fadeOut();
                $(suspendAction).append(loaderHtml).fadeIn();

                disableActions(confirmedId, true);
                disableLinks(true);

                $.getJSON('/server/' + PROJECT_ID + '/' + confirmedId + '/suspend_server/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            // Recall clicked action link on error
                            $(suspendAction).empty().fadeOut();
                            $(suspendAction).append(suspendHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var statusCell = '#' + confirmedId + '-status-cell';
                            var actionsCell = '#' + confirmedId + '-actions-cell';

                            // Update status and actions cells
                            $(statusCell).empty().fadeOut();
                            $(actionsCell).empty().fadeOut();
                            $(statusCell).append("SUSPENDED").fadeIn();
                            $(actionsCell).append(resumeHtml).fadeIn();
                        }

                        disableActions(confirmedId, false);
                        disableLinks(false);
                    })
                    .error(function () {
                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
                        $(suspendAction).empty().fadeOut();
                        $(suspendAction).append(suspendHtml).fadeIn();

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

    $(document).on('click', '.suspend-instance', function () {

        instanceId = $(this).parent().parent().attr('id');

        // Clear and add instance name to .instance-name span in confirm statement
        var nameSelector = '#' + instanceId + '-name-text';
        $('#instance-suspend-confirm-form > p > span.instance-name').empty().append($(nameSelector).text());

        $("#instance-suspend-confirm-form").dialog("open");
    });
});
