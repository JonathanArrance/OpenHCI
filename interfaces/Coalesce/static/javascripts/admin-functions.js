$(function () {

    // --
    var gettingPhonehomeMsg;
    $("#phonehome").click(function (event) {
        event.preventDefault();
        $("<div></div>")
            .prop("id", "phonehome-confirm-form")
            .prop("title", "Phone Home")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Send support data to TransCirrus?"))
            .dialog({
                autoOpen: true,
                height: 125,
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
                        var form = $("#phonehome-confirm-form");
                        message.showMessage('notice', "Phoning Home ...");
                        disableUiButtons('.ui-button', true);
                        form.empty()
                            .append($("<span></span>").addClass("ajax-loader-label").html("Working: ").fadeIn())
                            .append($("<div></div>").prop("id", 'loader').addClass("ajax-loader").fadeIn())
                            .append($("<p></p>").prop("id", "status").css("text-align", "center").html("Initializing Phone Home"));
                        form.dialog({height: 225});
                        var phonehome = $.getJSON('/phonehome/')
                            .done(function (data) {
                                if (data.status == "error") {
                                    message.showMessage('error', data.message);
                                    disableUiButtons('.ui-button', false);
                                    $("#phonehome-confirm-form").empty()
                                        .append($("<p></p>").css("text-align", "center").html("Send support data to TransCirrus?").fadeIn());
                                    form.dialog({height: 125});
                                }
                                if (data.status == "success") {
                                    message.showMessage('success', data.message);
                                    location.replace('coal/login.html');
                                }
                            })
                            .fail(function () {
                                message.showMessage('error', "Server Fault");
                                disableUiButtons('.ui-button', false);
                                $("#phonehome-confirm-form").empty()
                                    .append($("<p></p>").css("text-align", "center").html("Send support data to TransCirrus?").fadeIn());
                                form.dialog({height: 125});
                            });
                        gettingPhonehomeMsg = false;
                        var phonehomeMsg = window.setInterval(function () {
                            if (!gettingPhonehomeMsg) {
                                gettingPhonehomeMsg = true;
                                getMsg();
                            }
                        }, 5000);
                        $.when(phonehome).done(function () {
                            clearInterval(phonehomeMsg);
                        });
                    }
                }
            });
    });

    function getMsg() {
        var getMsg = $.getJSON('/phonehome/getmsg/')
            .done(function (data) {
                $("#status").html(data.message);
            });
        $.when(getMsg).always(function () {
            gettingPhonehomeMsg = false;
        });
    }
});