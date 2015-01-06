$(function() {

    var csrftoken = getCookie('csrftoken');

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

    $(function() {

        $( "#instance-view-power-confirm-form" ).dialog({
            autoOpen: false,
            height: 120,
            width: 350,
            modal: true,
            buttons: {
                "Confirm": function() {

                    message.showMessage('notice', 'Toggling server power.');

                    $.getJSON();

                    $(this).dialog( "close" );
                },
                Cancel: function() { $( this ).dialog( "close" ); }	// Close modal form
            },
            close: function() {	}
        });

        $('#power-server').click(function(){
            $( "#instance-power-cycle-confirm-form" ).dialog( "open" );
        });
    });
});