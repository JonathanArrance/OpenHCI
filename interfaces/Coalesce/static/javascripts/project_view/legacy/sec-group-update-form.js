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

    // Form Elements
    var ports = $("#update_ports");

    // Local Variables
    var id = '';
    var secGroup = '';
    var targetRow;

    // Widget Elements
    var progressbar = $("#secGroup_progressbar");

    $('#sec-group-update-form').dialog({
        autoOpen: false,
        height: 410,
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
            "Confirm": function () {

                // Confirmed Selections
                var confId = id,
                    confSecGroup = $(secGroup).text(),
                    confPorts = ports.val(),
                    confEnablePing = $('input[name=enable_ping]:checked').val(),
                    confTransport = $('input[name=update_transport]:checked').val();

                // Check defaults
                if (confPorts == "") { confPorts = "443,80,22"; }
                if (confEnablePing == undefined) { confEnablePing = 'true'; }
                if (confTransport == undefined) { confTransport = 'tcp'; }

                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                message.showMessage('notice', "Updating " + confSecGroup + ".");

                disableLinks(true);

                // Disable actions
                disableActions("update-secGroup", true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/update_security_group/' + confId + '/' + PROJECT_ID + '/' + confPorts + '/' + confEnablePing + '/' + confTransport + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();
                    })
                    .always(function () {

                        disableLinks(false);
                        disableActions("update-secGroup", false);
                        setVisible(progressbar, false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.update-secGroup', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        secGroup = document.getElementById(id + "-name-text");

        $('div#sec-group-update-form > p > span.secGroup-name').empty().append($(secGroup).text());

        $('#sec-group-update-form').dialog("open");
    });
});




