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
	
	var floating_ip = $( "#assign_floating_ip" ),
		instance = $( "#assign_instance" ),
		allFields = $( [] ).add( floating_ip ).add( instance ),
		tips = $( ".validateTips" );

	function updateTips( t ) {
		tips.text( t ).addClass( "ui-state-highlight" );
		setTimeout(function() {
			tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
	}

	function checkLength( o, n, min, max ) {
		if ( o.val().length > max || o.val().length < min ) {
			o.addClass( "ui-state-error" );
			updateTips( "Length of " + n + " must be between " +
				min + " and " + max + "." );
			return false;
		} else {
			return true;
		}
	}
	
	$( "#fip-assign-dialog-form" ).dialog({
		autoOpen: false,
		height: 300,
		width: 350,
		modal: true,
		buttons: {
			"Assign": function() {

				var bValid = true;
				allFields.removeClass( "ui-state-error" );

                var confirmedFipId = floating_ip.val();
                var confirmedInstanceId = instance.val();

				if ( bValid ) {

                    if ($('.allocate_ip').is(':visible')){ $('.allocate_ip').toggle(); }
                    if ($('#assign_ip').is(':visible')){ $('#assign_ip').toggle(); }

                    $('.disable-action').bind('click', false);
                    var origActionColor = $('.disable-action').css('color');
                    $('.disable-action').css('color', '#696969');

				   	$.getJSON('/assign_floating_ip/' + confirmedFipId + '/' + confirmedInstanceId + '/' + PROJECT_ID + '/')
				   	.success(function(data) {

				   		if (data.status == 'error') { 
				   			message.showMessage('error', data.message);
				   		};

				   		if (data.status == 'success') {

				   			message.showMessage('success', data.message);

				   			var targetSpan = document.getElementById(data.floating_ip+"-instance-name");
				   			var targetCell = document.getElementById(data.floating_ip+"-instance-cell");
				   			var targetActions = document.getElementById(data.floating_ip+"-actions-cell");
				   			var newName = '<span id="'+data.floating_ip+'-instance-name">'+data.instance_name+'</span>';
				   			var newActions = '<a href="#" id="'+data.floating_ip+'" class="unassign_ip">unassign</a>';

				   			$(targetSpan).fadeOut().remove();
				   			$(targetActions).empty().fadeOut();

				   			$(targetCell).append(newName).fadeIn();
				   			$(targetActions).append(newActions).fadeIn();

				   			var ipOption = 'select#assign_floating_ip option[value="'+data.floating_ip+'"]';
				   			$(ipOption).remove();

                            var instanceOption = 'select#assign_instance option[value="'+confirmedInstanceId+'"]';
                            $(instanceOption).remove();
				   		}

                        if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                        if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }
                        $('.disable-action').unbind('click', false);
                        $('.disable-action').css('color', origActionColor);
				   	})
				   	.error(function() { 

				   		message.showMessage('error', 'Server Fault');

                        if ($('.allocate_ip').is(':hidden')){ $('.allocate_ip').toggle(); }
                        if ($('#assign_ip').is(':hidden')){ $('#assign_ip').toggle(); }

                        $('.disable-action').unbind('click', false);
                        $('.disable-action').css('color', origActionColor);
				   	});

				    $( this ).dialog( "close" );
				}
			},
			Cancel: function() { $( this ).dialog( "close" ); }
			},
			close: function() { allFields.val( "" ).removeClass( "ui-state-error" ); }
		});

		$( "#assign_ip" ).click(function() {
			$( "#fip-assign-dialog-form" ).dialog( "open" );
		});
	});
});