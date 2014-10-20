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
		
		
		
		var
            security_group_rules = $( "#security_group_rules" ),
            security_groups = $( "#security_groups" ),
            cores = $("#cores"),
            fixed_ips = $("#fixed_ips"),
            floating_ips = $("#floating_ips"),
            injected_file_content_bytes = $("#injected_file_content_bytes"),
            injected_file_path_bytes = $("#injected_file_path_bytes"),
            injected_files = $("#injected_files"),
            instances = $("#instances"),
            key_pairs = $("#key_pairs"),
            metadata_items = $("#metadata_items"),
            ram = $("#ram"),
            storage = $("#storage"),
            snapshots = $("#snapshots"),
            volumes = $("#volumes"),
            subnets = $("#subnets"),
            networks = $("#networks"),
            routers = $("#routers"),
            ports = $("#ports"),

			allFields = $( [] ).add(security_group_rules).add(security_groups).add(cores).add(fixed_ips).add(floating_ips).add(injected_file_content_bytes).add(injected_file_path_bytes).add(injected_files).add(instances).add(key_pairs)
            .add(metadata_items).add(ram).add(storage).add(snapshots).add(volumes).add(subnets).add(networks).add(routers).add(ports),
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

	

		$( "#project-quota-form" ).dialog({
			autoOpen: false,
			height: 450,
			width: 350,
			modal: true,
			buttons: {
				"Create an instance": function() {
					var bValid = true;
					allFields.removeClass( "ui-state-error" );

					bValid = bValid && checkLength( name, "router_name", 3, 16 );

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

		$( "#project-quotas" )
			.click(function() {
				$( "#project-quota-form" ).dialog( "open" );
			});
			
			
	});
	});
