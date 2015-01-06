$(function () {

    var csrftoken = getCookie('csrftoken');
    var flavor = $("#flavor");

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#instance-view-resize-dialog-form").dialog({
        autoOpen: false,
        height: 350,
        width: 350,
        modal: true,
        buttons: {
            "Resize Instance": function () {

                var confirmedFlavor = $(flavor).find("option:selected");
                var status = $('#instance-status'), console = $('#instance-console');

                message.showMessage('notice', "Resizing " + $('#instance-name').text() + " to " + confirmedFlavor.text() + "." );

                $('#widget-actions').slideUp();

                // Initialize progressbar and make it visible if hidden
                $('#instance-progressbar').progressbar({value: false});
                setVisible('#instance-progressbar', true);

                emptyAndAppend(status, "RESIZE");

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/' + confirmedFlavor.val() + '/resize_server/')
                    .done(function (data) {

                        if (data.status == "error") {

                            message.showMessage('error', data.message);
                            emptyAndAppend(status, "ACTIVE");
                        }

                        if (data.status == "success") {

                            message.showMessage('success', data.message);
                            emptyAndAppend(status, "ACTIVE");
                            emptyAndAppend('#instance-flavor', confirmedFlavor);
                        }
                    })
                    .fail(function () {

                        message.showMessage('error', "Server Fault");
                        emptyAndAppend(status, "ERROR");
                    })
                    .always(function() {

                        $('#instance-console-refresh-confirm-form').dialog({
                            resizable: false,
                            autoOpen: false,
                            height: 150,
                            modal: true,
                            buttons: {
                                "Yes": function(){
                                    $( console ).attr( 'src', function ( i, val ) { return val; });
                                    $(this).dialog("close");
                                },
                                "No": function(){
                                    $(this).dialog("close");
                                }
                            },
                            close: function() { }
                        });

                        $('#widget-actions').slideDown();
                        setVisible('#instance-progressbar', false);
                    });

                $(this).dialog("close");
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {  }
    });

    $("#resize-server")
        .click(function () {
            $("#instance-view-resize-dialog-form").dialog("open");
        });
});
