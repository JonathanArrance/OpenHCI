$(function() {

    var message = new message_handle();	// Initialize message handling

    // must obtain csrf cookie for AJAX call
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    $(function() {

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        $( "#instance-view-power-confirm-form" ).dialog({
            autoOpen: false,
            height: 120,
            width: 350,
            modal: true,
            buttons: {
                "Confirm": function() {

                    message.showMessage('notice', 'Toggling server power.');

                    $.getJSON()

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