$(function() {
                var message = new message_handle();
               
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
                    message.showMessage('notice', 'Createing new volume '+volume_name.val());
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( volume_name, "volume_name", 3, 16 );
                    
					if ( bValid ) {
					   $.getJSON('/create_volume/' + volume_name.val() + '/' + volume_size.val() + '/' + description.val() + '/' + volume_type.val() + '/' + PROJECT_ID + '/'
                                                                ).success(function(data){
                                                                                if(data.status == 'error'){message.showMessage('error', data.message);}
                                                                                if(data.status == 'success'){
                                                                                                $('#volume_list')
                                                                                                .append('<tr><td><a href="/projects/'+PROJECT_ID+'/volumes/'+data.volume_id+'/view/">'+data.volume_name+'</a></td><td>None</td><td><a href="/delete_volume/'+data.volume_id+'/'+PROJECT_ID+'/">delete</a></td></tr>');
                                                                                                $('#att_volume')
                                                                                                .append('<option value="'+data.volume_id+'">'+data.volume_name+'</option>');
                                                                                                message.showMessage('success', data.message);
                                                                                }
                                                                }).error(function(){
                                                                                message.showMessage('error', 'Server Fault');
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
