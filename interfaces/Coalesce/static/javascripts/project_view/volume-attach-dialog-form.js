$(function () {

    var csrftoken = getCookie('csrftoken');
    var volumeId = '';  // Initialize empty string to hold ID of clicked volume
    var attachHtml = '<a href="#" class="attach-instance">attach</a>';
    var detachHtml = '<a href="#" class="detach-instance">detach</a>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#volume-attach-dialog-form").dialog({
        autoOpen: false,
        height: 210,
        width: 225,
        modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position:{
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        buttons: {
            "Attach Volume": function () {

                var confirmedId = volumeId;
                var volName = document.getElementById(confirmedId + "-name-text");
                volName = $(volName).text();
                var confirmedInstance = $('#instance').find("option:selected");
                var noticeMessage = 'Attaching ' + volName + ' to ' + confirmedInstance.text() + '.';

                message.showMessage('notice', noticeMessage);

                // Create loader
                var actionsCell = document.getElementById(confirmedId + "-actions-cell");
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/attach_volume/' + PROJECT_ID + '/' + confirmedInstance.val() + '/' + confirmedId)
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(attachHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(detachHtml).fadeIn();

                            var targetAttached = document.getElementById(confirmedId + "-attached-cell");
                            $(targetAttached).empty().fadeOut();
                            $(targetAttached).append(confirmedInstance.text()).fadeIn();
                        }
                    })
                    .error(function () {

                        message.showMessage('error', "Server Fault");

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(attachHtml);
                });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.attach-instance', function () {

        volumeId = $(this).parent().parent().attr('id');

        // Clear and add volume name to .volume-name span in confirm statement
        var nameSelector = '#' + volumeId + '-name-text';
        $('#volume-attach-dialog-form > p > span.volume-name').empty().append($(nameSelector).text());

        $("#volume-attach-dialog-form").dialog("open");
    });
});
