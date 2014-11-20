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
			height: 400,
			width: 350,
			modal: true,
			buttons: {
				"Detach Volume": function() {

					console.log("start");	// DEBUG

					var confirmedId = volumeId;														// Initialize string to hold ID of confirmed volume

					var confirmedNameSelector = '#'+confirmedId+'-name-text';						// Create string to target confirmed volume name-cell
					var confirmedName = $('#volume_list').find(confirmedNameSelector).text();		// Find confirmed volume name

					var noticeMessage = 'Detaching volume '+confirmedName+'.';						// Create notice message
					message.showMessage('notice', noticeMessage);									// Flag notice message

					console.log("notice generated");	// DEBUG

					// --- BEGIN Create loader
					// Target clicked action link
					var confirmedActionSelector = '#'+confirmedId+'-actions-cell > .detach-instance';

					var confirmedActionHtml = '<a href="#" class="detach-instance">detach</a>';		// Copy the html that link
					var loaderId = confirmedId+'-loader';											// Target new loader ID
					var loaderHtml = '<div class="ajax-loader" id="'+loaderId+'"></div>';			// New loader html

					// Clear clicked action link and replace with loader
					$(confirmedActionSelector).empty().fadeOut();
					$(confirmedActionSelector).append(loaderHtml).fadeIn();
					loaderId = '#'+loaderId;														// Update loader ID
					// --- END Create Loader

					console.log("loader created");	//DEBUG

					$.getJSON('/detach_volume/' + PROJECT_ID + '/' + volumeId + '/')
					.success(function(data){ 

						console.log("ajax success");

						console.log("success");	//DEBUG

							message.showMessage('notice', 'Detached '+confirmedName+'.');							// Flag success message

							var actionsSelector = '#'+confirmedId+'-actions-cell';					// Target actions-cell
                        	var attachAction = '<a href="#" class="attach-instance">attach</a>';	// New actions html string
   							var attachedSelector = '#'+confirmedId+'-attached-cell';
   							var placeholderHtml = '<span id="'+confirmedId+'-attached-placeholder">No Attached Instances</span>';


   							$(attachedSelector).fadeOut().empty();
   							$(attachedSelector).append(placeholderHtml).fadeIn();

   							// Update action cell							
                        	$(actionsSelector).fadeOut().empty();
                        	$(actionsSelector).append(attachAction).fadeIn();

						// // Check if instance was successfully paused
						// if(data.status == 'error'){ 

						// 	console.log("threw an error");	//DEBUG

						// 	message.showMessage('error', data.message);							// Flag error message

						// 	// Recall clicked action link on error
      //                   	$(confirmedActionSelector).empty().fadeOut();							
      //                		$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();
						// }

						// if(data.status == 'success'){ 											

						// 	console.log("success");	//DEBUG

						// 	message.showMessage('success', data.message);							// Flag success message

						// 	var actionsSelector = '#'+confirmedId+'-actions-cell';					// Target actions-cell
      //                   	var attachAction = '<a href="#" class="attach-instance">attach</a>';	// New actions html string
   			// 				var attachedSelector = '#'+confirmedId+'-attached-cell';
   			// 				var placeholderHtml = '<span id="'+confirmedId+'-attached-placeholder">No Attached Instances</span>';


   			// 				$(attachedSelector).fadeOut().empty();
   			// 				$(attachedSelector).append(placeholderHtml).fadeIn();

   			// 				// Update action cell							
      //                   	$(actionsSelector).fadeOut().empty();
      //                   	$(actionsSelector).append(attachAction).fadeIn();
      //                   }

                    })
                    .error(function(){

                    	console.log("server fault");	//DEBUG

                        message.showMessage('error', 'Server Fault');

                        // Recall clicked action link on server fault
						$(confirmedActionSelector).empty().fadeOut();
						$(confirmedActionSelector).append(confirmedActionHtml).fadeIn();
                        
					});

					$( this ).dialog( "close" );					// Close Modal Form
				},
				Cancel: function() { $( this ).dialog( "close" ); }	// Close Modal Form
			},
			close: function() {	}
		})

		// Open modal form when detach-instance button clicked
		$(document).on('click', '.detach-instance', function(){

			volumeId = $(this).parent().parent().attr('id');		// Get the ID of the instance that the user wishes to detach
						
			// Clear and add volume name to .volume-name span in confirm statement
			var nameSelector = '#'+volumeId+'-name-text';
			$('div#volume-detach-confirm-form > p > span.volume-name')
				.empty()
				.append($(nameSelector).text());

			$( "#volume-detach-confirm-form" ).dialog( "open" ); 	// Open Detach Confirm Form	
		});
	});
});
