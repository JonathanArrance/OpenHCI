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
		
		
		
		var 	sec_group_name = $( "#sec_group_name" ),
			sec_key_name = $( "#sec_key_name" ),
			image_name = $( "#image_name" ),
			name= $( "#name" ),
			network_name = $( "#network_name" ),
                        flavor_name = $( "#flavor_name"),

			allFields = $( [] ).add( sec_group_name ).add(sec_key_name).add(image_name).add(name).add(network_name),
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

	

		$( "#instance-dialog-form" ).dialog({
			autoOpen: false,
			height: 450,
			width: 350,
			modal: true,
			buttons: {
				"Create an instance": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( name, "image_name", 3, 16 );

					if ( bValid ) {
					  
					   $.post('/create_image/' + name.val() + '/' + sec_group_name.val() + '/nova/' + flavor_name.val() + '/' + sec_key_name.val() + '/' + image_name.val() + '/' + network_name.val() + '/' + PROJECT_ID + '/',
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

		$( "#create-instance" )
			.click(function() {
				$( "#instance-dialog-form" ).dialog( "open" );
			});
			
			
	});
	});
