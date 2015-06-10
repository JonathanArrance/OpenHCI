$(function () {
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
                        var phonehome = $.Deferred();

                        message.showMessage('notice', "Phoning Home ...");
                        disableUiButtons('.ui-button', true);
                        $("#phonehome-confirm-form").empty()
                            .append($("<div></div>").prop("id", 'loader').prop("class", "ajax-loader").fadeIn())
                            .append($("<p></p>").prop("id", "status"));

                        phonehome = $.getJSON('/phonehome/')
                            .done(function (data) {
                                if (data.status == "error") {
                                    message.showMessage('error', data.message);
                                    disableUiButtons('.ui-button', false);
                                    $("#phonehome-confirm-form").empty()
                                        .append($("<p></p>").css("text-align", "center").html("Send support data to TransCirrus?").fadeIn());
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
                            });

                        var phonehomeMsg = setInterval(getMsg(), 5000);

                        $.when(phonehome).done(function(){
                            clearInterval(phonehomeMsg);
                        });
                    }
                }
            });
    });

    function getMsg() {
        $.getJSON('/phonehome/getmsg/')
            .done(function (data) {
                console.log(data);
                $("#status").empty()
                    .append(data.msg)
            });
    }
});