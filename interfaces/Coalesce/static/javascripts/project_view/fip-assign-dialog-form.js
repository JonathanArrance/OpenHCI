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

    // Form Elements
    var floating_ip = $("#assign_floating_ip"),
        instance = $("#assign_instance");

    // Widget Elements
    var progressbar = $("#fip_progressbar");

    $("#fip-assign-dialog-form").dialog({
        autoOpen: false,
        height: 265,
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
            "Assign": function () {

                // Confirmed Selections
                var confIpId = floating_ip.val(),
                    confIp = $(document.getElementById(confIpId + "-ip-address")).text(),
                    confInstanceId = instance.val(),
                    targetRow = document.getElementById(confIpId);

                // Disable widget view links and hide widget buttons
                disableLinks(true);
                setVisible('#allocate_ip', false);
                setVisible('#assign_ip', false);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                disableProgressbar(progressbar, "fips", false);

                $.getJSON('/assign_floating_ip/' + confIp + '/' + confInstanceId + '/' + PROJECT_ID + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            // Update instance and action cells
                            var instanceCell = document.getElementById(data.floating_ip_id + "-instance-cell");
                            var actionsCell = document.getElementById(data.floating_ip_id + "-actions-cell");
                            var instanceHtml = '<span id="' + data.floating_ip_id + '-instance-name">' + data.instance_name + '</span>';
                            var newAction = '<a href="#" id="' + data.floating_ip_id + '" class="unassign_ip">unassign</a>';

                            $(instanceCell).empty().fadeOut();
                            $(actionsCell).empty().fadeOut();

                            $(instanceCell).append(instanceHtml).fadeIn();
                            $(actionsCell).append(newAction).fadeIn();

                            // Update assign_ip selects
                            removeFromSelect(data.floating_ip_id, floating_ip, assignableFips);
                            removeFromSelect(confInstanceId, instance, assignableInstances);

                            // Add assigned class
                            $(targetRow).addClass("fip-assigned");
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');
                    })
                    .always(function () {

                        // Reset interface
                        checkAssignFip();
                        disableProgressbar(progressbar, "fips", true);
                        setVisible('#allocate_ip', true);
                        disableLinks(false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#assign_ip").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        $("#fip-assign-dialog-form").dialog("open");
    });
});