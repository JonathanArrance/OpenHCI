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
		
		
		
		var 	net_name = $( "#net_name" ),
			admin_state = $( "#admin_state" ),
			shared = $( "#shared" ),
			allFields = $( [] ).add( net_name ).add( admin_state ).add( shared ),
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

	

		$( "#private-network-dialog-form" ).dialog({
			autoOpen: false,
			height: 350,
			width: 350,
			modal: true,
			buttons: {
				"Add a Private Network": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( net_name, "net_name", 3, 56 );

					if ( bValid ) {
					  
					   $.post('/add_private_network/' + net_name.val() + '/' + admin_state.val() + '/' + shared.val() + '/' + PROJECT_ID + '/');

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

		$( "#create-private-network" )
			.click(function() {
				$( "#private-network-dialog-form" ).dialog( "open" );
			});
			
			
	});
	});