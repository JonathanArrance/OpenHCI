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

    var actions = $('#widget-actions'),
        progressbar = $('#secGroup_progressbar');

    $("#update-security-group").dialog({
        autoOpen: false,
        height: 410,
        width: 235,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "top",
            at: "center",
            of: $('#page-content')
        },
        buttons: {
            "Update Security Group": function () {

                var confPorts = $("#update_ports").val(),
                    confEnablePing = $('input[name=enable_ping]:checked').val(),
                    confTransport = $('input[name=update_transport]:checked').val();

                message.showMessage('notice', "Updating security group.");

                // Hide other actions
                actions.slideUp();

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                $.getJSON('/update_security_group/' + GROUP_ID + '/' + PROJECT_ID + '/' + confPorts + '/' + confEnablePing + '/' + confTransport + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            updateSecGroupPorts(data.ports);

                            if (confTransport == 'tcp') {
                                updateTcpString();
                                $("#tcp_ports").html(tcpString);
                            }
                            if (confTransport == 'udp') {
                                updateUdpString();
                                $("#udp_ports").html(udpString);
                            }

                            updateIcmpString();
                            $("#icmp").html(icmpString);
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');
                    })
                    .always(function () {

                        actions.slideDown();
                        setVisible(progressbar, false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#update-secGroup").click(function (event) {

        event.preventDefault();

        $("#update-security-group").dialog("open");

        var radio = $('input[name=update_transport]:checked').val();

        if (radio == 'tcp') {
            $("#update_ports").val(tcpPorts);
        } else if (radio == 'udp') {
            $("#update_ports").val(udpPorts);
        }
    });

    $('input[name=update_transport]').change(function () {
        console.log("transport changed");
        var checked = $('input[name=update_transport]:checked').val();
        if (checked == 'tcp') {
            $("#update_ports").val(tcpPorts);
        } else if (checked == 'udp') {
            $("#update_ports").val(udpPorts);
        }
    })
});
