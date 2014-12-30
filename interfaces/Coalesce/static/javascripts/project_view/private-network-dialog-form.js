$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var privateNet = $("#privateNet_name"),
        admin_state = $("#admin_state"),
        shared = $("#shared"),
        allFields = $([]).add(privateNet).add(admin_state).add(shared),
        tips = $(".validateTips");

    // Widget Elements
    var progressbar = $("#privateNet_progressbar"),
        table =$("#privateNet_list");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#private-network-dialog-form").dialog({
        autoOpen: false,
        height: 350,
        width: 225,
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
            "Create Private Network": function () {

                allFields.removeClass("ui-state-error");
                $('.error').fadeOut().remove();

                var bValid = true;
                bValid = bValid &&
                    checkLength(tips, privateNet, "net name", 3, 16);

                if (bValid) {

                    // Confirmed Selections
                    var confShared = shared.val(),
                        confAdminState = admin_state.val();

                    message.showMessage('notice', 'Creating new router ' + privateNet.val());

                    setVisible("#create-private-network", false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

                    $.getJSON('/add_private_network/' + privateNet.val() + '/' + confAdminState + '/' + confShared + '/' + PROJECT_ID + '/')
                        .done(function(data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);
                            }
                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new network row
                                var newRow = '';
                                newRow +=
                                    '<tr id="' + data.net_id + '">' +
                                    '<td id="' + data.net_id + '-name-cell">' +
                                    '<a href="/network/' + data.net_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.net_id + '-name-text">' + data.net_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.net_id + '-status-cell">' +
                                    'shared: <span id="' + data.net_id + '-shared-text">' + confShared + '</span>' +
                                    '<span id="{{ value.net_id }}-status-pipe"> | </span>' +
                                    'admin state: <span id="' + data.net_id + '-admin-text">' + confAdminState + '</span></td>' +
                                    '<td id="' + data.net_id + '-subnet-cell"><span id="' + data.subnet.subnet_id + '">' + data.subnet.subnet_name + '</span></td>' +
                                    '<td id="' + data.net_id + '-actions-cell"><a href="#" class="delete-privateNet">delete</a></td>' + '</tr>';

                                // Check to see if this is the first network to be generated, if so remove placeholder
                                var rowCount = $("#privateNet_list tr").length;
                                if (rowCount > 2) {
                                    $("#privateNet_placeholder").remove().fadeOut();
                                }

                                // Append new row to router-list
                                table.append(newRow).fadeIn();
                            }

                        })
                        .fail(function() {

                            message.showMessage('error', 'Server Fault');	// Flag server fault message
                        })
                        .always(function() {

                            setVisible(progressbar, false);
                            setVisible('#create-private-network', true);
                            disableLinks(false);
                        });

                    $(this).dialog("close");

                    allFields.val("").removeClass("ui-state-error");
                    $(".error").fadeOut().remove();
                }
            }
        },
        close: function () {

            allFields.val("").removeClass("ui-state-error");
            $(".error").fadeOut().remove();
        }
    });

    $("#create-private-network")
        .click(function () {
            $("#private-network-dialog-form").dialog("open");
        });
});
