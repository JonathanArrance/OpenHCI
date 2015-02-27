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


    var id = '';
    var secGroup = '';
    var targetRow;

    // Widget Elements
    var progressbar = $("#secGroup_progressbar"),
        placeholder =
            '<tr id="#secGroup_placeholder"><td><p><i>You have no keys defined</i></p></td><td></td><td></td></tr>';

    $('#sec-group-delete-confirm-form').dialog({
        autoOpen: false,
        height: 125,
        width: 245,
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
                    confSecGroup = $(secGroup).text();

                var actionsCell = document.getElementById(confId + "-actions-cell");
                var actionsHtml = actionsCell.innerHTML;

                message.showMessage('notice', "Deleting " + confSecGroup + ".");

                disableLinks(true);

                // Disable router actions
                disableActions("delete-secGroup", true);

                // Initialize progressbar and make it visible if hidden
                $(progressbar).progressbar({value: false});
                setVisible(progressbar, true);

                // Create loader
                var loaderId = confId + '-loader';
                var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                // Clear clicked action link and replace with loader
                $(actionsCell).empty().fadeOut();
                $(actionsCell).append(loaderHtml).fadeIn();

                $.getJSON('/delete_sec_group/' + confId + '/' + PROJECT_ID + '/')
                    .done(function (data) {

                        if (data.status == 'error') {

                            message.showMessage('error', data.message);

                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        }

                        if (data.status == 'success') {

                            message.showMessage('success', data.message);

                            $(targetRow).fadeOut().remove();
                        }

                        // If last security group, reveal placeholder
                        var rowCount = $('#secGroup_list tr').length;
                        if (rowCount < 2) {
                            $('#secGroup_list').append(placeholder).fadeIn();
                        }

                        // Update selects
                        removeFromSelect(confSecGroup, $("#sec_group_name"), secGroupInstOpts);
                    })
                    .fail(function () {

                        message.showMessage('error', 'Server Fault');

                        $(actionsCell).empty().fadeOut();
                        $(actionsCell).append(actionsHtml).fadeIn();
                    })
                    .always(function () {

                        disableLinks(false);
                        disableActions("delete-secGroup", false);
                        setVisible(progressbar, false);
                    });

                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $(document).on('click', '.delete-secGroup', function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        targetRow = $(this).parent().parent();
        id = $(targetRow).attr("id");
        secGroup = document.getElementById(id + "-name-text");

        $('div#sec-group-delete-confirm-form > p > span.secGroup-name').empty().append($(secGroup).text());

        $('#sec-group-delete-confirm-form').dialog("open");
    });
});




