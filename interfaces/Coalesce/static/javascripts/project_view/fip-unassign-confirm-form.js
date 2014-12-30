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
        width: 185,
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

                var actionsCell = document.getElementById(confFipId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                // Disable widget view links and hide assign_ip button
                disableLinks(true);
                setVisible('#assign_ip', false);

                // Initialize progressbar and make it visible
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

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

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml);
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            var instanceCell = document.getElementById(data.floating_ip_id + "-instance-cell");
                            var instanceNameHtml = '<span id="' + data.floating_ip_id + '-instance-name">None</span>';
                            var newActions = '<a href="#" class="deallocate_ip">deallocate</a>';

                            $(instanceCell).empty().fadeOut();
                            $(actionsCell).empty().fadeOut();

                            $(instanceCell).append(instanceNameHtml).fadeIn();
                            $(actionsCell).append(newActions).fadeIn();

                            var ipOption = '<option value="' + data.floating_ip_id + '">' + data.floating_ip + '</option>';
                            $('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(ipOption);

                            var instanceOption = '<option value="' + confInstanceId + '">' + confInstanceName + '</option>';
                            $('div#fip-assign-dialog-form > form > fieldset > select#assign_instance').append(instanceOption);

                            $(targetRow).removeClass("fip-assigned");
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml);
                    })
                    .always(function () {

                        setVisible(progressbar, false);
                        setVisible('#assign_ip', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },

        close: function () {
        }
    });

    $(document).on('click', '.unassign_ip', function () {

        event.preventDefault();

        targetRow = $(this).parent().parent();
        fipId = $(targetRow).attr("id");
        fip = $(document.getElementById(fipId + "-ip-address")).text();
        instanceName = $(document.getElementById(fipId + "-instance-name")).text();
        instanceId = $('a').filter(function () {
            return $(this).text() == instanceName;
        });
        instanceId = $(instanceId).parent().parent().attr("id");

        $('div#fip-unassign-confirm-form > p > span.ip-address').empty().append(fip);

        $('#fip-unassign-confirm-form').dialog("open");
    });
});