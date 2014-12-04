$(function () {

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var floating_ip = $("#assign_floating_ip"),
        instance = $("#assign_instance");

    $("#fip-assign-dialog-form").dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
            "Assign": function () {

                var bValid = true;
                var confirmedId = floating_ip.val();
                var confirmedInstanceId = instance.val();

                if (bValid) {

                    setVisible('.allocate_ip', false);
                    setVisible('#assign_ip', false);
                    disableLinks(true);

                    $.getJSON('/assign_floating_ip/' + confirmedId + '/' + confirmedInstanceId + '/' + PROJECT_ID + '/')
                        .success(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                var instanceName = document.getElementById(data.floating_ip + "-instance-name");
                                var instanceCell = document.getElementById(data.floating_ip + "-instance-cell");
                                var actionsCell = document.getElementById(data.floating_ip + "-actions-cell");
                                var instanceNameHtml = '<span id="' + data.floating_ip + '-instance-name">' + data.instance_name + '</span>';
                                var unassignHtml = '<a href="#" id="' + data.floating_ip + '" class="unassign_ip">unassign</a>';

                                $(instanceName).fadeOut().remove();
                                $(actionsCell).empty().fadeOut();

                                $(instanceCell).append(instanceNameHtml).fadeIn();
                                $(actionsCell).append(unassignHtml).fadeIn();

                                var ipOption = 'select#assign_floating_ip option[value="' + data.floating_ip + '"]';
                                $(ipOption).remove();

                                var instanceOption = 'select#assign_instance option[value="' + confirmedInstanceId + '"]';
                                $(instanceOption).remove();
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

                    $(this).dialog("close");
                }
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#assign_ip").click(function () {
        $("#fip-assign-dialog-form").dialog("open");
    });
});