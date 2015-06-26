$(function () {

    var instance = $("#assign_instance"),
        allFields = $([]).add(instance),
        tips = $(".validateTips");

    $("#fip-view-assign-dialog-form").dialog({
        autoOpen: false,
        height: 400,
        width: 350,
        modal: true,
        buttons: {
            "Assign": function () {
                var bValid = true;
                allFields.removeClass("ui-state-error");
                if (bValid) {
                    $.post('/assign_floating_ip/' + FIP + '/' + instance.val() + '/' + PROJECT_ID + '/',
                        function () {
                            location.reload();
                        });

                    $(this).dialog("close");
                }
            },
            Cancel: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
            allFields.val("").removeClass("ui-state-error");
        }
    });

    $("#view-assign_ip")
        .click(function () {
            $("#fip-view-assign-dialog-form").dialog("open");
        });
});
