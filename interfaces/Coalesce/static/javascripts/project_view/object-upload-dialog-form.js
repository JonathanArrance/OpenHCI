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

        var container = $("#upload_obj_cont"),
            import_local = $("#import_local"),
			allFields = $([]).add(container).add(import_local),
			tips = $(".validateTips");

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
                updateTips("Length of " + n + " must be between " +
					min + " and " + max + ".");
                return false;
            } else
            {
                return true;
            }
        }

        function convertURL(url)
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

        $("#object-upload-dialog-form").dialog(
        {
            autoOpen: false,
            height: 400,
            width: 350,
            modal: true,
        resizable: false,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "center",
            at: "center",
            of: $('#page-content')
        },
            buttons:
            {
                "Upload object": function ()
                {
                    var bValid = true;
                    allFields.removeClass("ui-state-error");

                    bValid = bValid && checkLength(container, "container", 3, 16);
                    var progress_id = "feedface";

                    var filename = import_local.val();

                    // URL to send our data to. Note: the progress id must be the 8th param so the progress updater can find it.
                    var url = "/upload_local_object/" + container.val() + "/" + filename + "/" + PROJECT_ID + "/" + PROJECT + "/" + "na" + "/" + "na" + "/" + progress_id + "/";

                    // Send the form data via the ajax call and setup the function that will update the progress bar.
                    var form_data = new FormData($('#object-upload-form')[0]);
                    form_data.append("project_id", PROJECT_ID);
                    form_data.append("project", PROJECT);
                    form_data.append("progress_id", progress_id);
                    $.ajax(
                        {
                            type: 'POST',
                            url: url,
                            data: form_data,
                            contentType: false,
                            cache: false,
                            processData: false,
                            async: true,                    // must be true to get updated with the progress of the upload
                            //xhr: function ()
                            //{
                            //    // This function will be called during the upload to update the progress of the upload.
                            //    var bar = $('#object-upload-dialog-form').find('#upload_bar');
                            //    var percent = $('#object-upload-dialog-form').find('#upload_percent');

                            //    var xhr = $.ajaxSettings.xhr();
                            //    xhr.upload.onprogress = function (e)
                            //    {
                            //        if (e.lengthComputable)
                            //        {
                            //            var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                            //            percentage = percentage + "%";
                            //            bar.width(percentage)
                            //            percent.html(percentage);
                            //        }
                            //    };
                            //    return xhr;
                            //},
                            success: function (data)
                            {
                                // This function is called if the post was successful to the server (not the upload).
                                // Convert the data into something we can use.
                                var ret_data = JSON.parse(data);

                                if (ret_data.status == "error")
                                {
                                    // There was an error on the server uploading the file so display the error message.
                                    message.showMessage("error", ret_data.message);
                                    $("#object-upload-dialog-form").dialog("close");
                                    return;
                                }

                                // The upload was successful so add the table entry, display a message to the user and close the dialog box.
                                console.log('success: object_id:' + ret_data.object_id);
                                $('#object_list')
                                .append('<tr><td>' + display_name + '</td><td><a href="/delete_object/' + ret_data.object_id + '/">delete</a></td></tr>');
                                message.showMessage("success", ret_data.message);
                                $("#object-upload-dialog-form").dialog("close");
                            },
                            error: function (data)
                            {
                                // This function is called if there was an issue posting the data to the server.
                                message.showMessage("error", "Server Fault");
                                $("#object-upload-dialog-form").dialog("close");
                            }
                        });
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

        $("#upload-object")
			.click(function ()
			{
			    $("#object-upload-dialog-form").dialog("open");
			});
    });
});
