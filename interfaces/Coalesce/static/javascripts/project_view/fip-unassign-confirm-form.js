$(function() { 

	var message = new message_handle();	// Initialize message 

	var targetRow;
	var fip = '';
	var fipId = '';
	var instanceName = '';
	var instanceId = '';

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
	
	$( "#fip-unassign-confirm-form" ).dialog({
		autoOpen: false,
		height: 150,
		width: 350,
		modal: true,
		buttons: {
			"Confirm": function() {

				var bValid = true;
				var confirmedFip = fip;
				var confirmedFipId = fipId;

				if ( bValid ) {

					$('#assign_ip').attr("disabled", true);
					$('.allocate_ip').attr("disabled", true);

					// --- BEGIN Create loader
					// Target clicked action link
				   	var targetActions = document.getElementById(confirmedFip+"-actions-cell");

					var confirmedActionHtml = '<a href="#" id="'+confirmedFip+'" class="unassign_ip">unassign</a>';		// Copy the html that link
					var loaderId = confirmedFip+'-loader';											// Target new loader ID
					var loaderHtml = '<div class="ajax-loader" id="'+confirmedFip+'"></div>';			// New loader html

					// Clear clicked action link and replace with loader
					$(targetActions).empty().fadeOut();
					$(targetActions).append(loaderHtml).fadeIn();
					loaderId = '#'+loaderId;														// Update loader ID
					// --- END Create Loader

				   	$.getJSON('/unassign_floating_ip/' + confirmedFipId + '/')
				   	.success(function(data) {

				   		if (data.status == 'error') { 
				   			message.showMessage('error', data.message); 

				   			$(targetActions).empty().fadeOut();
				   			$(targetActions).append(confirmedActionHtml);
				   		};

				   		if (data.status == 'success') {

				   			message.showMessage('success', data.message);

				   			var targetSpan = document.getElementById(data.floating_ip+"-instance-name");
				   			var targetCell = document.getElementById(data.floating_ip+"-instance-cell");
				   			var newName = '<span id="'+data.floating_ip+'-instance-name">None</span>';
				   			var newActions = '<a href="#" id="'+data.floating_ip+'" class="deallocate_ip">deallocate</a>';

				   			$(targetSpan).fadeOut().remove();
				   			$(targetActions).empty().fadeOut();

				   			$(targetCell).append(newName).fadeIn();
				   			$(targetActions).append(newActions).fadeIn();

				   			var ipOption = '<option value="'+data.floating_ip+'">'+data.floating_ip+'</option>';
				   			$('div#fip-assign-dialog-form > form > fieldset > select#assign_floating_ip').append(ipOption);

                            var instanceOption = '<option value="'+instanceId+'">'+instanceName+'</option>';
                            $('div#fip-assign-dialog-form > form > fieldset > select#assign_instance').append(instanceOption);
				   		}

				   		$('#assign_ip').attr("disabled", false);
						$('.allocate_ip').attr("disabled", false);
				   	})
				   	.error(function() { 

				   		message.showMessage('error', 'Server Fault'); 

				   		$(targetActions).empty().fadeOut();
				   		$(targetActions).append(confirmedActionHtml);

				   		$('#assign_ip').attr("disabled", false);
						$('.allocate_ip').attr("disabled", false);
				   	});

				    $( this ).dialog( "close" );
				}
			},
			Cancel: function() { $( this ).dialog( "close" ); }
			},
			close: function() { }
		});

		$(document).on('click', '.unassign_ip', function(){

			targetRow = $(this).parent().parent();
			fip = $(this).attr("id");
			fipId = $(targetRow).attr("class");
			instanceName = document.getElementById(fip+"-instance-name");
			instanceName = $(instanceName).text();
			instanceId = $('a').filter(function(index) {
				return $(this).text() == instanceName;
			});
			instanceId = $(instanceId).parent().parent().attr("id");

			$('div#fip-unassign-confirm-form > p > span.ip-address')
				.empty()
				.append(fip);

			$('#fip-unassign-confirm-form').dialog("open");
		});
	});
});