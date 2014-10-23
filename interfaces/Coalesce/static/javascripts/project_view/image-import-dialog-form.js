$(function ()
{
    var message = new message_handle();

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

                    // Save the image name for later use.
                    display_name = image_name.val();

                    if (image_type.val() == "image_url")
                    {
                        // The user wants to upload a remote image via the supplied URL.
                        if (!valid_URL(import_remote))
                            return;

                        // Start the progress bar function so it can start querying the server for status.
                        startProgressBarUpdate(progress_id);

                        // All the data is good so post the data to the server.
                        image_location = import_remote;

                        loc = image_location.val();
                        image_location = convert_URL(image_location);
                        loc = loc.replace(/\//g, '&47');

                        url = '/import_remote/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/';

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
                            async: true,                    // must be true to get updated with the progress of the upload
                            success: function (data)
                            {
                                // This function is called if the post was successful to the server (not the upload).
                                // Convert the data into something we can use.
                                var ret_data = JSON.parse(data);

                                if (ret_data.status == "error")
                                {
                                    // There was an error on the server uploading the file so display the error message.
                                    message.showMessage("error", ret_data.message);
                                    return;
                                }

                                // The upload was successful so add the table entry, display a message to the user and close the dialog box.
                                //var ret_data = JSON.parse(data);
                                console.log('success: image_id:' + ret_data.image_id);
                                $('#image_list')
                                .append('<tr><td>' + display_name + '</td><td><a href="/delete_image/' + ret_data.image_id + '/">delete</a></td></tr>');
                                message.showMessage("success", ret_data.message);
                                $("#image-import-dialog-form").dialog("close");
                            },
                            error: function (data)
                            {
                                // This function is called if there was an issue posting the data to the server.
                                message.showMessage("error", "Server Fault");
                                $("#image-import-dialog-form").dialog("close");
                            }
                        });
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
                        var url = '/import_local/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/';

                        // Send the form data via the ajax call and setup the function that will update the progress bar.
                        var form_data = new FormData($('#image-upload-form')[0]);
                        $.ajax(
                        {
                            type: 'POST',
                            url: url,
                            data: form_data,
                            contentType: false,
                            cache: false,
                            processData: false,
                            async: true,                    // must be true to get updated with the progress of the upload
                            xhr: function ()
                            {
                                // This function will be called during the upload to update the progress of the upload.
                                var bar = $('#image-import-dialog-form').find('#upload_bar');
                                var percent = $('#image-import-dialog-form').find('#upload_percent');

                                var xhr = $.ajaxSettings.xhr();
                                xhr.upload.onprogress = function (e)
                                {
                                    if (e.lengthComputable)
                                    {
                                        var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                                        percentage = percentage + "%";
                                        bar.width(percentage)
                                        percent.html(percentage);
                                    }
                                };
                                return xhr;
                            },
                            success: function (data)
                            {
                                // This function is called if the post was successful to the server (not the upload).
                                // Convert the data into something we can use.
                                var ret_data = JSON.parse(data);

                                if (ret_data.status == "error")
                                {
                                    // There was an error on the server uploading the file so display the error message.
                                    message.showMessage("error", ret_data.message);
                                    return;
                                }

                                // The upload was successful so add the table entry, display a message to the user and close the dialog box.
                                console.log('success: image_id:' + ret_data.image_id);
                                $('#image_list')
                                .append('<tr><td>' + display_name + '</td><td><a href="/delete_image/' + ret_data.image_id + '/">delete</a></td></tr>');
                                message.showMessage("success", ret_data.message);
                                $("#image-import-dialog-form").dialog("close");
                            },
                            error: function (data)
                            {
                                // This function is called if there was an issue posting the data to the server.
                                message.showMessage("error", "Server Fault");
                                $("#image-import-dialog-form").dialog("close");
                            }
                        });
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

// This function will update the progress bar every second with the progress of the remote upload.
// The progress is determined by querying the server for the current progress.
var g_progress_intv = 0;
function startProgressBarUpdate(upload_id)
{
    var bar = $('#image-import-dialog-form').find('#upload_bar');
    var percent = $('#image-import-dialog-form').find('#upload_percent');

    if (g_progress_intv != 0)
        clearInterval(g_progress_intv);

    g_progress_intv = setInterval(function ()
    {
        $.getJSON("/get_upload_progress/" + upload_id, function (data)
        {
            if (data.status == "error")
            {
                // We got an error back so display the message and stop updating the progress bar.
                var message = new message_handle();
                message.showMessage("error", data.message);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                return;
            }

            if (data.length == -1)
            {
                percentage = "100%";
                bar.width(percentage)
                percent.html(percentage);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                return;
            }
            length = parseInt(data.length);
            if (length > 0)
                var percentage = Math.floor(100 * parseInt(data.uploaded) / length);
            else
                var percentage = 0;
            percentage = percentage + "%";
            bar.width(percentage)
            percent.html(percentage);
        });
    }, 1000);
    return;
}
