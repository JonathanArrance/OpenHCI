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

		var tips = $( ".validateTips" );

		function updateTips( t ) {
			tips.text( t ).addClass( "ui-state-highlight" );
			setTimeout(function() { tips.removeClass( "ui-state-highlight", 1500 ); }, 500 );
		}

		$( "#volume-detach-confirm-form" ).dialog({
			autoOpen: false,
			height: 150,
			width: 350,
			modal: true,
			buttons: {
				"Detach Volume": function() {

					var confirmedVolumeId = volumeId;
					var confirmedVolumeName = document.getElementById(confirmedVolumeId+"-name-text");
					confirmedVolumeName = $(confirmedVolumeName).text();
					var noticeMessage = 'Detaching volume '+confirmedVolumeName+'.';	

					message.showMessage('notice', noticeMessage);	

					// --- BEGIN Create loader

					// Target clicked action link
					var targetActions = document.getElementById(confirmedVolumeId+"-actions-cell");

					// Copy the html that link
					var confirmedActionHtml = '<a href="#" class="detach-instance">detach</a>';

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

					$.getJSON('/detach_volume/' + PROJECT_ID + '/' + confirmedVolumeId + '/')
					.success(function(data){

                        console.log(data);

						if (data.status == 'error') {

							message.showMessage('error', data.message);

							$(targetActions).empty().fadeOut();
							$(targetActions).append(confirmedActionHtml).fadeIn();
						};

						if (data.status == 'success') {

							message.showMessage('success', data.message);

							var newAction = '<a href="#" class="attach-instance">attach</a>';
							$(targetActions).empty().fadeOut();
							$(targetActions).append(newAction).fadeIn();

							var targetAttached = document.getElementById(confirmedVolumeId+"-attached-cell");
							$(targetAttached).empty().fadeOut();
							$(targetAttached).append("No Attached Instance").fadeIn();
						};
                    })
                    .error(function(){

                        message.showMessage('error', 'Server Fault');

						$(targetActions).empty().fadeOut();
						$(targetActions).append(confirmedActionHtml).fadeIn();
                        
					});

					$( this ).dialog( "close" );					// Close Modal Form
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close Modal Form
			},
			close: function() {	}
		})

		// Open modal form when detach-instance button clicked
		$(document).on('click', '.detach-instance', function(){

            // Get the ID of the instance that the user wishes to detach
			volumeId = $(this).parent().parent().attr('id');
						
			// Clear and add volume name to .volume-name span in confirm statement
			var nameSelector = '#'+volumeId+'-name-text';
			$('div#volume-detach-confirm-form > p > span.volume-name')
				.empty()
				.append($(nameSelector).text());

			$( "#volume-detach-confirm-form" ).dialog( "open" ); 	// Open Detach Confirm Form	
		});
	});
});
