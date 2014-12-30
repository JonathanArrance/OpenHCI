$(function () {

    var csrftoken = getCookie('csrftoken');
    var volumeId = '';  // Initialize empty string to hold ID of clicked volume
    var detachHtml = '<a href="#" class="detach-instance">detach</a>';
    var attachHtml = '<a href="#" class="attach-instance">attach</a>';

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#volume-detach-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 230,
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
            "Detach Volume": function () {

                var confirmedId = volumeId;
                var volName = document.getElementById(confirmedId + "-name-text");
                    volName = $(volName).text();
                var noticeMessage = 'Detaching volume ' + volName + '.';

                message.showMessage('notice', noticeMessage);

                // Create loader
                var actionsCell = document.getElementById(confirmedId + "-actions-cell");
                var loaderId = confirmedId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/detach_volume/' + PROJECT_ID + '/' + confirmedId + '/')
                    .success(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(detachHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(attachHtml).fadeIn();

                            var targetAttached = document.getElementById(confirmedId + "-attached-cell");
                            $(targetAttached).empty().fadeOut();
                            $(targetAttached).append("No Attached Instance").fadeIn();
                        }
                    })
                    .error(function () {

                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(detachHtml).fadeIn();
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    })

    $(document).on('click', '.detach-instance', function () {

        volumeId = $(this).parent().parent().attr('id');

        // Clear and add volume name to .volume-name span in confirm statement
        var nameSelector = '#' + volumeId + '-name-text';
        $('div#volume-detach-confirm-form > p > span.volume-name').empty().append($(nameSelector).text());

        $("#volume-detach-confirm-form").dialog("open");
    });
});