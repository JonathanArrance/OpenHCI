$(function() {

	var message = new message_handle();	// Initialize message handling
	var instanceId = '';				// Initialize empty string to hold ID of clicked instance

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

		$( "#instance-pause-confirm-form" ).dialog({
			autoOpen: false,
			height: 150,
			width: 250,
			modal: true,
			buttons: {
				"Confirm": function() {

					var confirmedId = instanceId;						// Initialize string to hold ID of confirmed instance
					message.showMessage('notice', 'Pausing Instance');	// Flag notice

					// Create loader
					var confirmedActionSelector = '#'+confirmedId+'-actions-cell > .pause-instance';	// Target clicked action link
					var confirmedActionHtml = '<a href="#" class="pause-instance">pause</a>';			// Copy the html that link
					var loaderId = confirmedId+'-loader';												// Target new loader ID
					var loaderHtml = '<div class="ajax-loader" id="'+loaderId+'"></div>';				// New loader html

					// Clear clicked action link and replace with loader
					$(confirmedActionSelector).empty().fadeOut();
					$(confirmedActionSelector).append(loaderHtml).fadeIn();
					loaderId = '#'+loaderId;															// Update loader ID

					$.getJSON('/server/' + PROJECT_ID + '/' + confirmedId + '/pause_server/')
						.success(function(data){

							// Check if instance was successfully paused
                        	if(data.status == 'error'){ 
                        		message.showMessage('error', data.message);								// Flag error message

                        		// Recall clicked action link on error
                        		$(confirmedActionSelector).empty().fadeOut();							
                        		$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();
                        	}

                        	if(data.status == 'success'){ 												// Update interface

                        		message.showMessage('success', data.message);							// Flag success message

                        		var statusSelector = '#'+confirmedId+'-status-cell';					// Target instance-status-cell
                        		var actionsSelector = '#'+confirmedId+'-actions-cell';					// Target instance-actions-cell

                        		// New actions html string
                        		var unpauseAction = '<a href="#" class="unpause-instance">unpause</a>';

                        		// Update status and actions cells
                        		$(statusSelector).fadeOut().empty();							
                        		$(actionsSelector).fadeOut().empty();
                        		$(statusSelector).append("PAUSED").fadeIn();
                        		$(actionsSelector).append(unpauseAction).fadeIn();
                        	}
                        })
						.error(function(){ 
							message.showMessage('error', 'Server Fault'); 						// Flag server fault message

							// Recall clicked action link on server fault
							$(confirmedActionSelector).empty().fadeOut();
							$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();
					});			

					$( this ).dialog( "close" );						// Close modal form	
				},
				Cancel: function() { $( this ).dialog( "close" ); }		// Close modal form	
			}
		})

		// Open modal form when pause-instance button clicked
		$(document).on('click', '.pause-instance', function(){

			instanceId = $(this).parent().parent().attr('id');		// Get the ID of the instance that the user wishes to pause
						
			// Clear and add instance name to .instance-name span in confirm statement
			var nameSelector = '#'+instanceId+'-name-text';
			$('#instance-pause-confirm-form > p > span.instance-name')
				.empty()
				.append($(nameSelector).text());

			$( "#instance-pause-confirm-form" ).dialog( "open" ); 	// Open Pause Confirm Form	
		});
	});
});
