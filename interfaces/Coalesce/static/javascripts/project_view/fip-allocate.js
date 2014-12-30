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
    var id;

    // Widget Elements
    var progressbar = $("#fip_progressbar"),
        table = $("#fip_list");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $("#allocate_ip").click(function () {

        setVisible('#allocate_ip', false);
        setVisible('#assign_ip', false);
        disableLinks(true);

        // Initialize progressbar and make it visible if hidden
        $(progressbar).progressbar({value: false});
        setVisible(progressbar, true);

        $.getJSON('/allocate_floating_ip/' + PROJECT_ID + '/' + extNet + '/')
            .done(function (data) {

                if (data.status == 'error') {

                    message.showMessage('error', data.message);
                }

                if (data.status == 'success') {

                    message.showMessage('success', "Successfully allocated " + data.ip_info.floating_ip + ".");

                    var newRow = '';    // Initialize empty string for new instance row
                    newRow +=
                        '<tr id="' + data.ip_info.floating_ip_id + '">' +
                        '<td id="' + data.ip_info.floating_ip_id + '-ip-cell">' +
                        '<a href="/floating_ip/' + data.ip_info.floating_ip_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                        '<span id="' + data.ip_info.floating_ip_id + '-ip-address">' + data.ip_info.floating_ip + '</span></a></td>' +
                        '<td id="' + data.ip_info.floating_ip_id + '-instance-cell"><span id="' + data.ip_info.floating_ip_id + '-instance-name">None</span></td>' +
                        '<td id="' + data.ip_info.floating_ip_id + '-actions-cell"><a href="#" " class="deallocate_ip">deallocate</a></td>' +
                        '</tr>';

                    // If first fip, remove placeholder
                    var rowCount = $('#fip_list tr').length;
                    if (rowCount <= 2) {
                        $('#fip_placeholder').remove().fadeOut();
                    }

                    // Append new row to instance-list
                    $(table).append(newRow).fadeIn();

                    var newOption = '<option value="' + data.ip_info.floating_ip_id + '">' + data.ip_info.floating_ip + '</option>';
                    $('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(newOption);
                }
            })
            .fail(function () {

                message.showMessage('error', 'Server Fault');
            })
            .always(function () {

                setVisible(progressbar, false);
                setVisible('#allocate_ip', true);
                setVisible('#assign_ip', true);
                disableLinks(false);
            });
    });
});