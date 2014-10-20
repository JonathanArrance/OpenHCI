$(function ()
{
    // must obtain csrf cookie for AJAX call
    function getCookie(name)
    {
        var cookieValue = null;
        if (document.cookie && document.cookie != '')
        {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++)
            {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '='))
                {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    $(function ()
    {
        function csrfSafeMethod(method)
        {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        $.ajaxSetup(
        {
            crossDomain: false, // obviates need for sameOrigin test
            beforeSend: function (xhr, settings)
            {
                if (!csrfSafeMethod(settings.type))
                {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        //$("#X-Progress-ID").val(guid());

        var image_name = $("#import_img_name"),
			disk_format = $("#import_img_disk"),
			container_format = $("#import_img_cont"),
            image_type = $("#import_img_type"),
            import_local = $("#import_local"),
            import_remote = $("#import_remote"),
            visibility = $("#import_img_vis");
        //progress_id = $("#X-Progress-ID");
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
            // Validate the length of the image name.
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
            // Validate a given URL is correct.
            var urlregex = new RegExp("^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$");
            if (urlregex.test(url.val()))
            {
                return (true);
            }
            alert("invalid url " + url.val());
            url.addClass("ui-state-error");
            updateTips("Invalid remote URL.");
            return (false);
        }

        function convert_URL(url)
        {
            // Convert a URL from having /s to %47.
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


        function S4()
        {
            // Generate a random number string for use in a guid.
            return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
        }

        function guid()
        {
            // Generate a guid without the dashes.
            return (S4() + S4() + S4() + "4" + S4().substr(0, 3) + S4() + S4() + S4() + S4()).toLowerCase();
        }

        $("#image-import-dialog-form").dialog(
        {
            autoOpen: false,
            height: 600,
            width: 350,
            modal: true,
            buttons:
            {
                "Import image": function ()
                {
                    allFields.removeClass("ui-state-error");

                    // Make sure the image name is of the proper size of 3 to 20 characters.
                    // TODO: Need to see why there is a 3 - 20 size limit!!!
                    // This is the name of the image to be shown in the UI; not the one being uploaded.
                    if (!checkLength(image_name, "image_name", 3, 20))
                        return;

                    progress_id = guid();

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

                        $.post('/import_remote/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/')
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

                        startProgressBarUpdate(progress_id);

                        // We don't care what the local filename or path is for local files so we just use na
                        // to keep from having to convert /'s to %47.
                        loc = "na"

                        // Save the image name for later use.
                        display_name = image_name.val();

                        // Build the url that we will use to send the form data. The file contents are handled seperately.
                        var url = '/import_local/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/';

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
                            async: true,
                            xhr: function ()
                            {
                                //var bar = $('.bar');
                                //var percent = $('.percent');
                                var bar = $('#image-import-dialog-form').find('#local_bar');
                                var percent = $('#image-import-dialog-form').find('#local_percent');

                                var xhr = $.ajaxSettings.xhr();
                                xhr.upload.onprogress = function (e)
                                {
                                    if (e.lengthComputable)
                                    {
                                        var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                                        percentage = percentage + "%";
                                        bar.width(percentage)
                                        percent.html("<center>" + percentage + "</center>");
                                    }
                                };
                                return xhr;
                            },
                            success: function (data)
                            {
                                console.log("Success");
                                var ret_data = JSON.parse(data);
                                console.log('success: image_id:' + ret_data.image_id);
                                $('#image_list')
                                .append('<tr><td>' + display_name + '</td><td><a href="/delete_image/' + ret_data.image_id + '/">delete</a></td></tr>');
                                $("#image-import-dialog-form").dialog("close");
                                alert("New local image " + display_name + " uploaded.");
                            },
                            error: function (data)
                            {
                                console.log('Error:' + data);
                                location.reload();
                            }
                        });
                        //$(this).dialog("close");
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

var g_progress_intv = 0;
function startProgressBarUpdate(upload_id)
{
    console.log("In startProgressBarUpdate, upload_id: " + upload_id);

    var bar = $('#image-import-dialog-form').find('#remote_bar');
    var percent = $('#image-import-dialog-form').find('#remote_percent');

    percentage = "10%";
    bar.width(percentage)
    percent.html("<center>" + percentage + "</center>");

    if (g_progress_intv != 0)
        clearInterval(g_progress_intv);

    var i = 2;
    g_progress_intv = setInterval(function ()
    {
        if (i == 10)
        {
            percentage = "100%";
            bar.width(percentage)
            percent.html("<center>" + percentage + "</center>");

            clearInterval(g_progress_intv);
            g_progress_intv = 0;
            return;
        }

        var percentage = 10 * i;
        i = i + 1;
        percentage = percentage + "%";
        bar.width(percentage)
        percent.html("<center>" + percentage + "</center>");

        //        $.getJSON("/get_upload_progress/" + upload_id, function (data)
        //        {
        //            if (data == null)
        //            {
        //              $("#uploadprogressbar").progressbar("value", 100);
        //              clearInterval(g_progress_intv);
        //              g_progress_intv = 0;
        //              return;
        //            }
        //            var percentage = Math.floor(100 * parseInt(data.uploaded) / parseInt(data.length));
        //            $("#uploadprogressbar").progressbar("value", percentage);
        //        });
    }, 1000);

    return;
}
