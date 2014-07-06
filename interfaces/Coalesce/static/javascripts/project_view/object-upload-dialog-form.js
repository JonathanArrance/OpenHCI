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
		
		var 	container = $( "#upload_obj_cont" ),
                        obj = $( "#upload_obj" ),
			allFields = $( [] ).add( container ).add( obj ),
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
                
                function convertURL( url ) {
                        for ( var i = 0; i < url.length; i++ ) {
                                if ( url[ i ] == '/' ) {
                                                url = url.substr( 0, i ) + "%47" + url.substr( i, url.length + 1 );
                                                i = i + 2;
                                }
                        }
                        return url;
                }

		$( "#object-upload-dialog-form" ).dialog({
			autoOpen: false,
			height: 400,
			width: 350,
			modal: true,
			buttons: {
				"Upload object": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( container, "container", 3, 16 );
					if ( bValid ) {
					  
					   $.post('/upload_object/' + container.val() + '/' + obj + '/' + PROJECT_ID + '/' + PROJECT + '/',
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

		$( "#upload-object" )
			.click(function() {
				$( "#object-upload-dialog-form" ).dialog( "open" );
			});
			
			
	});
	});
