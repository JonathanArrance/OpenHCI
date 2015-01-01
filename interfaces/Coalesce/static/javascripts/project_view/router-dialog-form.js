$(function () {

    var csrftoken = getCookie('csrftoken');

    // Dialog Form Elements
    var router_name = $("#router_name"),
        priv_net = $("#priv_net"),
        allFields = $([]).add(router_name).add(priv_net),
        tips = $(".validateTips");

    // Widget Elements
    var progressbar = $("#router_progressbar"),
        table = $('#router_list');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#router-dialog-form").dialog({
        autoOpen: false,
        height: 400,
        width: 235,
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
            "Create Router": function () {

                allFields.removeClass("ui-state-error");
                $('.error').fadeOut().remove();

                var bValid = true;
                bValid =
                    bValid &&
                    checkLength(tips, router_name, "router_name", 3, 16);

                if (bValid) {

                    var confPrivateNet = priv_net.val();

                    message.showMessage('notice', 'Creating new router ' + router_name.val());

                    setVisible("#create-router", false);
                    disableLinks(true);

                    // Initialize progressbar and make it visible if hidden
                    $(progressbar).progressbar({value: false});
                    setVisible(progressbar, true);

                    $.getJSON('/create_router/' + router_name.val() + '/' + confPrivateNet + '/' + DEFAULT_PUBLIC + '/' + PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                            }
                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Initialize empty string for new router row
                                var newRow = '';
                                newRow +=
                                    '<tr id="' + data.router_id + '">' +
                                    '<td id="' + data.router_id + '-name-cell">' +
                                    '<a href="/router/' + data.router_id + '/view/" class="disable-link disabled-link" style="color:#696969;">' +
                                    '<span id="' + data.router_id + '-name-text">' + data.router_name + '</span>' + '</a></td>' +
                                    '<td id="' + data.router_id + '-status-cell"><span id="' + data.router_id + '-status-text">ACTIVE</span></td>' +
                                    '<td id="' + data.router_id + '-actions-cell"><a href="#" class="delete-router">delete</a></td>' + '</tr>';

                                // Check to see if this is the first router to be generated, if so remove placeholder and reveal delete-router button
                                var rowCount = $("#router_list tr").length;
                                if (rowCount <= 2) {
                                    $("#router_placeholder").remove().fadeOut();
                                }

                                // Append new row to router-list
                                table.append(newRow).fadeIn();

                                // Add to routers
                                routers.setItem(
                                    data.router_id,
                                    { name: data.router_name, network: confPrivateNet }
                                );

                                // Update private network
                                privateNetworks.items[confPrivateNet].router = data.router_id;
                            }
                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');
                        })
                        .always(function () {

                            setVisible(progressbar, false);
                            setVisible('#create-router', true);
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

    $("#create-router")
        .click(function () {
            $("#router-dialog-form").dialog("open");
        });
});
