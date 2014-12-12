$(function () {

    var csrftoken = getCookie('csrftoken');
    var targetRow;
    var fip = '';
    var fipId = '';
    var instanceName = '';
    var instanceId = '';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

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

                var bValid = true;
                var confirmedFip = fip;
                var confirmedId = fipId;

                if (bValid) {

                    setVisible('#assign_ip', false);
                    disableLinks(true);

                    // Create loader
                    var actionsCell = document.getElementById(confirmedFip + "-actions-cell");
                    var unassignHtml = '<a href="#" id="' + confirmedFip + '" class="unassign_ip">unassign</a>';
                    var loaderId = confirmedFip + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/unassign_floating_ip/' + confirmedId + '/')
                        .success(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(unassignHtml);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var instanceName = document.getElementById(data.floating_ip + "-instance-name");
                                var instanceCell = document.getElementById(data.floating_ip + "-instance-cell");
                                var instanceNameHtml = '<span id="' + data.floating_ip + '-instance-name">None</span>';
                                var deallocateHtml = '<a href="#" id="' + data.floating_ip + '" class="deallocate_ip">deallocate</a>';

                                $(instanceName).fadeOut().remove();
                                $(actionsCell).empty().fadeOut();

                                $(instanceCell).append(instanceNameHtml).fadeIn();
                                $(actionsCell).append(deallocateHtml).fadeIn();

                                var ipOption = '<option value="' + data.floating_ip + '">' + data.floating_ip + '</option>';
                                $('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(ipOption);

                                var instanceOption = '<option value="' + instanceId + '">' + instanceName + '</option>';
                                $('div#fip-assign-dialog-form > form > fieldset > select#assign_instance').append(instanceOption);
                            }

                            setVisible('#assign_ip', true);
                            disableLinks(false);
                        })
                        .error(function () {

                            message.showMessage('error', 'Server Fault');

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(unassignHtml);

                            setVisible('#assign_ip', true);
                            disableLinks(false);
                        });

                    $(this).dialog("close");
                }
            }
        },

        close: function () {
        }
    });

    $(document).on('click', '.unassign_ip', function () {

        event.preventDefault();

        targetRow = $(this).parent().parent();
        fip = $(this).attr("id");
        fipId = $(targetRow).attr("class");
        instanceName = document.getElementById(fip + "-instance-name");
        instanceName = $(instanceName).text();
        instanceId = $('a').filter(function () {
            return $(this).text() == instanceName;
        });
        instanceId = $(instanceId).parent().parent().attr("id");

        $('div#fip-unassign-confirm-form > p > span.ip-address').empty().append(fip);

        $('#fip-unassign-confirm-form').dialog("open");
    });
});