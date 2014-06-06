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
		
		var 	image_name = $( "#import_img_name" ),
			container_format = $( "#import_img_cont" ),
			disk_format = $( "#import_img_disk" ),
                        image_type = $( "#import_img_type" ),
                        image_location = $( "#import_img_location" ),
                        visibility = $( "#import_img_vis" ),
			allFields = $( [] ).add( image_name ).add( container_format ).add( disk_format ).add( image_location ).add( visibility ),
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

		$( "#image-import-dialog-form" ).dialog({
			autoOpen: false,
			height: 400,
			width: 350,
			modal: true,
			buttons: {
				"Import image": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( image_name, "image_name", 3, 16 );
                                        //image_location = convertURL( image_location );
                                        var loc = "";
                                        loc = image_location.val();
                                        loc = loc.replace(/\//g, '%47');
					if ( bValid ) {
					  
					   $.post('/import_image/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/'); 
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

		$( "#import-image" )
			.click(function() {
				$( "#image-import-dialog-form" ).dialog( "open" );
			});
			
			
	});
	});
