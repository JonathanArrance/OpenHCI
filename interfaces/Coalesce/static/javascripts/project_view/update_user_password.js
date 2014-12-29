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
		
		
		
		var 	password1 = $( "#password1" ),
			password2 = $( "#password2" ),
			allFields = $( [] ).add( password1 ).add( password2 ),
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

		function checkRegexp( o, regexp, n ) {
			if ( !( regexp.test( o.val() ) ) ) {
				o.addClass( "ui-state-error" );
				updateTips( n );
				return false;
			} else {
				return true;
			}
		}

		$( "#dialog-form-update-password" ).dialog({
			autoOpen: false,
			height: 350,
			width: 350,
			modal: true,
            resizable: false,
            closeOnEscape: true,
            draggable: true,
            show: "fade",
            position:{
                my: "center",
                at: "center",
                of: $('#page-content')
            },
			buttons: {
				"Update Password": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( password1, "password1", 5, 16 );

					//bValid = bValid && (password1 == password2);


					if ( bValid ) {
					  
						$.post('/update_user_password/' + USER_ID + '/' + password1.val() + '/' + PROJECT_ID + '/',
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

		$( "#update-user-password" )
			.click(function() {
				$( "#dialog-form-update-password" ).dialog( "open" );
			});
			
			
	});
	});
