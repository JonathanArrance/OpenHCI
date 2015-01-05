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

    $("#project-delete-confirm-form").dialog({
        autoOpen: false,
        height: 125,
        width: 235,
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
            "Confirm": function () {

                message.showMessage('notice', "Deleting Project");

                disableUiButtons('.ui-button', true);

                $.getJSON('/projects/'+PROJECT_ID+'/'+PROJECT+'/delete/')
                    .done(function(data){
                        if (data.status == "error") {
                            message.showMessage('error', data.message);
                            disableUiButtons('.ui-button', false);
                        }
                        if (data.status == "success") {
                            message.showMessage('success', data.message);
                            location.replace('/cloud/manage');
                        }
                    })
                    .fail(function(){
                        disableUiButtons('.ui-button', false);
                    })
            },
            Cancel: function () {
                $(this).dialog("close");
            }	// Close modal form
        },
        close: function () {
        }
    });

    // Open modal form when delete-project button clicked
    $("#delete-project").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        $("#project-delete-confirm-form").dialog("open");
    });
});