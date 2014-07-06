$(function() {  
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
		
		var 	volume_name = $( "#volume_name" ),
			volume_size = $( "#volume_size" ),
			description = $( "#description" ),
                        volume_type = $( "#volume_type" ),
			allFields = $( [] ).add( volume_name ).add( volume_size ).add( description ).add( volume_type ),
			tips = $( ".validateTips" );

		function updateTips( t ) {
			tips
				.text( t )
				.addClass( "ui-state-highlight" );
			setTimeout(function() {
				tips.removeClass( "ui-state-highlight", 1500 );
			}, 500 );
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

		$( "#volume-dialog-form" ).dialog({
			autoOpen: false,
			height: 450,
			width: 350,
			modal: true,
			buttons: {
				"Create a volume": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( volume_name, "volume_name", 3, 16 );
                    
					if ( bValid ) {
					  
					   $.post('/create_volume/' + volume_name.val() + '/' + volume_size.val() + '/' + description.val() + '/' + volume_type.val() + '/' + PROJECT_ID + '/',
                                                                function(){
                                                                                location.reload();
                                                                }); 
					   $( this ).dialog( "close" );
					}
				},
				Cancel: function() {
					$( this ).dialog( "close" );
				}
			},
			close: function() {
				allFields.val( "" ).removeClass( "ui-state-error" );
			}
		});

		$( "#create-volume" )
			.click(function() {
				$( "#volume-dialog-form" ).dialog( "open" );
			});
			
			
	});
	});
