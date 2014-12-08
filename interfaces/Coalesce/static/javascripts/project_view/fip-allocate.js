$(function () {

    var csrftoken = getCookie('csrftoken');
    var extNet = $('.allocate_ip').attr("id");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $(".allocate_ip").click(function () {

        setVisible('.allocate_ip', false);
        setVisible('#assign_ip', false);
        disableLinks(true);

        // Initialize progressbar and make it visible if hidden
        $('#fip_progressbar').progressbar({value: false});
        setVisible('#fip_progressbar', true);

        $.getJSON('/allocate_floating_ip/' + PROJECT_ID + '/' + extNet + '/')
            .success(function (data) {

                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    message.showMessage('success', "Successfully allocated " + data.ip_info.floating_ip + ".");

                    var newRow = '';    // Initialize empty string for new instance row
                        newRow +=
                            '<tr id="' + data.ip_info.floating_ip + '">' +
                                '<td id="' + data.ip_info.floating_ip + '-ip-cell">' +
                                    '<a href="/floating_ip/' + data.ip_info.floating_ip_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.ip_info.floating_ip + '-ip-address">' + data.ip_info.floating_ip + '</span></a></td>' +
                                '<td id="' + data.ip_info.floating_ip + '-instance-cell"><span id="' + data.ip_info.floating_ip + '-instance-name">None</span></td>' +
                                '<td id="' + data.ip_info.floating_ip + '-actions-cell"><a id="' + data.ip_info.floating_ip + '" class="deallocate_ip" href="#">deallocate</a></td>' +
                            '</tr>';

                    // If first fip, remove placeholder
                    var rowCount = $('#fip_list tr').length;
                    if (rowCount <= 2) {
                        $('#fip_placeholder').remove().fadeOut();
                    }

                    // Append new row to instance-list
                    $('#fip_list').append(newRow).fadeIn();

                    var newOption = '<option value="' + data.ip_info.floating_ip + '">' + data.ip_info.floating_ip + '</option>';
                    $('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(newOption);
                }

                setVisible('#fip_progressbar', false);
                setVisible('.allocate_ip', true);
                setVisible('#assign_ip', true);
                disableLinks(false);
            })
            .error(function () {

                message.showMessage('error', 'Server Fault');

                setVisible('#fip_progressbar', false);
                setVisible('.allocate_ip', true);
                setVisible('#assign_ip', true);
                disableLinks(false);
        });
    });
});