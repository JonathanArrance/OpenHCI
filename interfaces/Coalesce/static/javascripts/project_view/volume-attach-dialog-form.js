$(function() {

	var message = new message_handle();	// Initialize message handling
	var volumeId = '';					// Initialize empty string to hold ID of clicked volume

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

		var instance = $( "#instance" ),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		$( "#volume-attach-dialog-form" ).dialog({
			autoOpen: false,
			height: 250,
			width: 350,
			modal: true,
			buttons: {
				"Attach Volume": function() {

					var confirmedVolumeId = volumeId;
					var confirmedVolumeName = document.getElementById(confirmedVolumeId+"-name-text");
					confirmedVolumeName = $(confirmedVolumeName).text();
                    var confirmedInstance = $("#instance").find(":selected");
					var confirmedInstanceId = confirmedInstance.val();
					var confirmedInstanceName = document.getElementById(confirmedInstanceId+"-name-text");
					confirmedInstanceName = $(confirmedInstanceName).text();
					var noticeMessage = 'Attaching '+confirmedVolumeName+' to '+confirmedInstanceName+'.';

					message.showMessage('notice', noticeMessage);

					// --- BEGIN Create loader

					// Target clicked action link
					var targetActions = document.getElementById(confirmedVolumeId+"-actions-cell");

					// Copy the html that link
					var confirmedActionHtml = '<a href="#" class="attach-instance">attach</a>';

					// Target new loader ID
					var loaderId = confirmedVolumeId+'-loader';		

					// New loader html
					var loaderHtml = '<div class="ajax-loader" id="'+loaderId+'"></div>';

					// Clear clicked action link and replace with loader
					$(targetActions).empty().fadeOut();
					$(targetActions).append(loaderHtml).fadeIn();

					// Update loader ID
					loaderId = '#'+loaderId;

					// --- END Create Loader

					$.getJSON('/attach_volume/' + PROJECT_ID + '/' + confirmedInstanceId + '/' + confirmedVolumeId)
					.success(function(data){
						if (data.status == 'error') {

							message.showMessage('error', data.message);

							$(targetActions).empty().fadeOut();
							$(targetActions).append(confirmedActionHtml).fadeIn();
						};

						if (data.status == 'success') {

							message.showMessage('success', data.message);

							var newAction = '<a href="#" class="detach-instance">detach</a>';
							$(targetActions).empty().fadeOut();
							$(targetActions).append(newAction).fadeIn();

							var targetAttached = document.getElementById(confirmedVolumeId+"-attached-cell");
							$(targetAttached).empty().fadeOut();
							$(targetAttached).append(confirmedInstanceName).fadeIn();
						};
					})
                    .error(function(){

                    	message.showMessage('error', "Server Fault");

                    	$(targetActions).empty().fadeOut();
						$(targetActions).append(confirmedActionHtml);
					});

					$( this ).dialog( "close" );					// Close Modal Form
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close Modal Form
			},
			close: function() {	}
		})

		// Open modal form when attach-instance button clicked
		$(document).on('click', '.attach-instance', function(){

			volumeId = $(this).parent().parent().attr('id');		// Get the ID of the instance that the user wishes to attach
						
			// Clear and add volume name to .volume-name span in confirm statement
			var nameSelector = '#'+volumeId+'-name-text';
			$('#volume-attach-dialog-form > p > span.volume-name')
				.empty()
				.append($(nameSelector).text());

			$( "#volume-attach-dialog-form" ).dialog( "open" ); 	// Open Pause Confirm Form	
		});
	});
});
