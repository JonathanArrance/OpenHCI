$(function () {
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

    $(function () {
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup(
        {
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        var image_name = $("#import_img_name"),
			disk_format = $("#import_img_disk"),
			container_format = $("#import_img_cont"),
            image_type = $("#import_img_type"),
            import_local = $("#import_local"),
            import_remote = $("#import_remote"),
            visibility = $("#import_img_vis");
        var tips = $(".validateTips");
        var image_location = "";

        var allFields = $([]).add(image_name).add(disk_format).add(container_format).add(image_type).add(image_location).add(visibility);

        function updateTips(t)
        {
            tips
				.text(t)
				.addClass("ui-state-highlight");
            setTimeout(function ()
            {
                tips.removeClass("ui-state-highlight", 1500);
            }, 500);
        }

        function checkLength(o, n, min, max)
        {
            if (o.val().length > max || o.val().length < min)
            {
                o.addClass("ui-state-error");
                updateTips("Length of " + n + " must be between " + min + " and " + max + ".");
                return false;
            }
            else
            {
                return true;
            }
        }

        function valid_URL(url)
        {
            alert("url = " + url.val());
            var urlregex = new RegExp("^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$");
            if (urlregex.test(url.val()))
            {
                alert("valid url");
                return (true);
            }
            alert("invalid url " + url.val());
            url.addClass("ui-state-error");
            updateTips("Invalid remote URL.");
            return (false);
        }

        function convert_URL(url)
        {
            for (var i = 0; i < url.length; i++)
            {
                if (url[i] == '/')
                {
                    url = url.substr(0, i) + "%47" + url.substr(i, url.length + 1);
                    i = i + 2;
                }
            }
            return url;
        }

        $("#image-import-dialog-form").dialog(
        {
            autoOpen: false,
            height: 500,
            width: 350,
            modal: true,
            buttons:
            {
                "Import image": function ()
                {
                    allFields.removeClass("ui-state-error");

                    // Make sure the image name is of the proper size 3 to 16 characters.
                    // This is the name of the image to be shown in the UI; not the one being uploaded.
                    if (!checkLength(image_name, "image_name", 3, 16))
                        return;

                    if (image_type.val() == "image_url")
                    {
                        // The user wants to upload a remote image via the supplied URL.
                        if (!valid_URL(import_remote))
                            return;

                        // All the data is good so post the data to the server.
                        image_location = import_remote;

                        loc = image_location.val();
                        image_location = convert_URL(image_location);
                        loc = loc.replace(/\//g, '&47');

                        $.post('/import_remote/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/')
                              .success(function (data)
                              {
                                  console.log('success: image_id:' + data.image_id);
                                  $('#image_list')
                                          .append('<tr><td>' + image_name.val() + '</td><td><a href="/delete_image/' + data.image_id + '/">delete</a></td></tr>');
                                  alert("New remote image " + data.image_name + " uploaded.");
                              })
                              .error(function ()
                              {
                                  console.log('Error:' + data);
                                  location.reload();
                              });
                        $(this).dialog("close");
                    }

                    else
                    {
                        // The user wants to upload a local image from this computer/laptop.
                        if (import_local.val().length == 0)
                        {
                            import_local.addClass("ui-state-error");
                            updateTips("A local file must be selected.");
                            return;
                        }

                        // We don't care what the local filename or path is for local files so we just use na
                        // to keep from having to convert /'s to %47.
                        loc = "na"

                        // Build the url that we will use to send the form data. The file contents are handled seperately.
                        var url = '/import_local/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/';

                        // Send the form data via the ajax call.
                        var form_data = new FormData($('#image-upload-form')[0]);
                        $.ajax(
                        {
                            type: 'POST',
                            url: url,
                            data: form_data,
                            contentType: false,
                            cache: false,
                            processData: false,
                            async: false,
                            success: function (data)
                            {
                                var ret_data = JSON.parse(data);
                                console.log('success: image_id:' + ret_data.image_id);
                                $('#image_list')
                                .append('<tr><td>' + image_name.val() + '</td><td><a href="/delete_image/' + ret_data.image_id + '/">delete</a></td></tr>');
                                alert("New local image " + ret_data.image_name + " uploaded.");
                            },
                            error: function (data)
                            {
                                console.log('Error:' + data);
                                location.reload();
                            }
                        });
                        $(this).dialog("close");
                    }
                },
                Cancel: function ()
                {
                    $(this).dialog("close");
                }
            },
            close: function ()
            {
                allFields.val("").removeClass("ui-state-error");
            }
        });

        $("#import-image")
			.click(function ()
            {
			    $("#image-import-dialog-form").dialog("open");
			});
    });
});
