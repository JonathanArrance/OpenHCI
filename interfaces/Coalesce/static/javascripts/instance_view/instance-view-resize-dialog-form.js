$(function () {

    var csrftoken = getCookie('csrftoken');
    var flavor = $("#flavor"),
        allFields = $([]).add(flavor);

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

                $.getJSON('/server/' + PROJECT_ID + '/' + SERVER_ID + '/' + confirmedFlavor.val() + '/resize_server/')
                    .success(function (data) {
                        console.log("JSON DATA: " + data);
                    })
                    .error(function () {
                        console.log("error");
                    });


                $(this).dialog("close");
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
        }
    });

    $("#resize-server")
        .click(function () {
            $("#instance-view-resize-dialog-form").dialog("open");
        });
});
