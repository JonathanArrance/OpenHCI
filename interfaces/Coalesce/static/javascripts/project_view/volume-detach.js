$(function() {  
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

		var     instance = $( "#det_instance" ),
                        volume = $( "#det_volume" ),

			allFields = $( [] ).add( instance ).add( volume ),
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

		//$( "#volume-detach-dialog-form" ).dialog({
		//	autoOpen: false,
		//	height: 400,
		//	width: 350,
		//	modal: true,
		//	buttons: {
		//		"Detach volume": function() {
		//			var bValid = true;
		//			allFields.removeClass( "ui-state-error" );

		//			if ( bValid ) {
         //                       $.getJSON('/detach_volume/' + PROJECT_ID + '/' + volume.val() + '/'
        //                                                        ).success(function(data){
        //                                                                        $('#volume_list')
        //                                                                       .append('<tr><td><a href="/projects/'+PROJECT_ID+'/volumes/'+data.volume_id+'/view/">'+data.volume_name+'</a></td><td>None</td><td><a href="/delete_volume/'+data.volume_id+'/'+PROJECT_ID+'/">delete</a></td></tr>');
        //                                                                        alert("Volume " + data.volume_name + " detached from "+instance.val()+".");
        //                                                        }).error(function(){
        //                                                        location.reload();
        //                                        });;

		//				$( this ).dialog( "close" );
                                                //$( "#vol_progressbar" ).progressbar({
                                                //                value: false
                                                //});

					//}
				//},
				//Cancel: function() {
				//	$( this ).dialog( "close" );
				//}
			//},
			//close: function() {
			//	allFields.val( "" ).removeClass( "ui-state-error" );
			//}
		//});

		$( "#detach-volume" )
			.click(function() {
				//$( "#volume-detach-dialog-form" ).dialog( "open" );
                $.getJSON('/detach_volume/' + PROJECT_ID + '/' + volume.val() + '/'
                                                                ).success(function(data){
                                                                                $('#volume_list')
                                                                                .append('<tr><td><a href="/projects/'+PROJECT_ID+'/volumes/'+data.volume_id+'/view/">'+data.volume_name+'</a></td><td>None</td><td><a href="/delete_volume/'+data.volume_id+'/'+PROJECT_ID+'/">delete</a></td></tr>');
                                                                                alert("Volume " + data.volume_name + " detached from "+instance.val()+".");
                                                                }).error(function(){
                                                                location.reload();
                                                });;
			});
	});
	});
