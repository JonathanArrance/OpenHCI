$(function () {

    // CSRF Protection
    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Local Variables
    var uploading = false;

    // Form Elements
    var image_name = $("#import_img_name"),
        disk_format = $("#import_img_disk"),
        container_format = $("#import_img_cont"),
        image_type = $("#import_img_type"),
        import_local = $("#import_local"),
        import_remote = $("#import_remote"),
        visibility = $("#import_img_vis"),
        image_location = "",
        allFields = $([]).add(image_name).add(disk_format).add(container_format).add(image_type).add(import_local).add(import_remote).add(image_location).add(visibility);

    $("#image-import-dialog-form").dialog(
        {
            autoOpen: false,
            height: 550,
            width: 235,
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
            buttons: {
                "Import Image": function () {

                    if (uploading) {
                        return;
                    }

                    // Remove UI validation flags
                    clearUiValidation(allFields);

                    // Make sure the image name is of the proper size of 3 to 20 characters.
                    // TODO: Need to see why there is a 3 - 20 size limit!!!
                    // This is the name of the image to be shown in the UI; not the one being uploaded.
                    if (!checkLength(image_name, "image_name", 3, 20))
                        return;

                    var progress_id = guid();

                    // Save the image name for later use.
                    var display_name = image_name.val();

                    if (image_type.val() == "image_url") {
                        // The user wants to upload a remote image via the supplied URL.
                        if (!checkUrl(import_remote))
                            return;

                        disableFormInputs('image', [ 'text', 'select', 'file'], true);
                        disableLinks(true);

                        // Start the progress bar function so it can start querying the server for status.
                        startProgressBarUpdate(progress_id);

                        // All the data is good so post the data to the server.
                        image_location = import_remote;

                        var loc = image_location.val();
                        image_location = convertUrl47(image_location);
                        loc = loc.replace(/\//g, '&47');

                        url = '/import_remote/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/';

                        // Send the form data via the ajax call.
                        uploading = true;
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
                                success: function (data) {
                                    // This function is called if the post was successful to the server (not the upload).
                                    // Convert the data into something we can use.
                                    var ret_data = JSON.parse(data);

                                    if (ret_data.status == "error") {
                                        // There was an error on the server uploading the file so display the error message.
                                        message.showMessage("error", ret_data.message);
                                        return;
                                    }

                                    var newRow =
                                        '<tr id="' + ret_data.image_id + '"><td id="' + ret_data.image_id + '-name-cell">' +
                                        '<span id="' + ret_data.image_id + '-name-text">' + display_name + '</span></td>' +
                                        '<td id="' + ret_data.image_id + '-actions-cell"><a href="#" class="delete-image">delete</a></td></tr>';

                                    // The upload was successful so add the table entry, display a message to the user and close the dialog box.
                                    //var ret_data = JSON.parse(data);
                                    console.log('success: image_id:' + ret_data.image_id);
                                    $('#image_list').append(newRow);

                                    message.showMessage("success", ret_data.message);

                                    $("#image-import-dialog-form").dialog("close");
                                    disableFormInputs('image', [ 'text', 'select', 'file'], false);
                                    disableLinks(false);
                                    uploading = false;
                                },
                                error: function () {

                                    // This function is called if there was an issue posting the data to the server.
                                    message.showMessage("error", "Server Fault");

                                    $("#image-import-dialog-form").dialog("close");
                                    disableFormInputs('image', [ 'text', 'select', 'file'], false);
                                    disableLinks(false);
                                    uploading = false;
                                }
                            });
                    }

                    else {
                        // The user wants to upload a local image from this computer/laptop.
                        if (!checkFile(import_local)) {
                            return;
                        }

                        disableUiButtons('.ui-dialog-titlebar-close', false);
                        disableLinks(true);

                        // We don't care what the local filename or path is for local files so we just use na
                        // to keep from having to convert /'s to %47.
                        loc = "na";

                        // Build the url that we will use to send the form data. The file contents are handled seperately.
                        var url = '/import_local/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + progress_id + '/';

                        // Send the form data via the ajax call and setup the function that will update the progress bar.
                        uploading = true;
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
                                xhr: function () {
                                    // This function will be called during the upload to update the progress of the upload.
                                    var bar = $('#image-import-dialog-form').find('#upload_bar');
                                    var percent = $('#image-import-dialog-form').find('#upload_percent');
                                    disableFormInputs('image', [ 'text', 'select', 'file'], true);

                                    var xhr = $.ajaxSettings.xhr();
                                    xhr.upload.onprogress = function (e) {
                                        if (e.lengthComputable) {
                                            var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                                            percentage = percentage + "%";
                                            bar.width(percentage);
                                            percent.html(percentage);
                                        }
                                    };
                                    return xhr;
                                },
                                success: function (data) {
                                    // This function is called if the post was successful to the server (not the upload).
                                    // Convert the data into something we can use.
                                    var ret_data = JSON.parse(data);

                                    if (ret_data.status == "error") {
                                        // There was an error on the server uploading the file so display the error message.
                                        message.showMessage("error", ret_data.message);
                                        return;
                                    }

                                    var newRow =
                                        '<tr id="' + ret_data.image_id + '"><td id="' + ret_data.image_id + '-name-cell">' +
                                        '<span id="' + ret_data.image_id + '-name-text">' + display_name + '</span></td>' +
                                        '<td id="' + ret_data.image_id + '-actions-cell"><a href="#" class="delete-image">delete</a></td></tr>';

                                    // The upload was successful so add the table entry, display a message to the user and close the dialog box.
                                    console.log('success: image_id:' + ret_data.image_id);
                                    $('#image_list').append(newRow);

                                    message.showMessage("success", ret_data.message);

                                    $("#image-import-dialog-form").dialog("close");
                                    disableFormInputs('image', [ 'text', 'select', 'file'], false);
                                    disableLinks(false);
                                    uploading = false;
                                },
                                error: function () {

                                    // This function is called if there was an issue posting the data to the server.
                                    message.showMessage("error", "Server Fault");

                                    $("#image-import-dialog-form").dialog("close");
                                    disableFormInputs('image', [ 'text', 'select', 'file'], false);
                                    disableLinks(false);
                                    uploading = false;
                                }
                            });
                    }
                }
            },
            close: function () {
                if (!uploading) {
                    resetUiValidation(allFields);
                }
            }
        });

    $("#import-image")
        .click(function () {
            $("#image-import-dialog-form").dialog("open");
        });
});

// This function will update the progress bar every second with the progress of the remote upload.
// The progress is determined by querying the server for the current progress.
var g_progress_intv = 0;
function startProgressBarUpdate(upload_id) {
    var bar = $('#image-import-dialog-form').find('#upload_bar');
    var percent = $('#image-import-dialog-form').find('#upload_percent');

    if (g_progress_intv != 0)
        clearInterval(g_progress_intv);

    g_progress_intv = setInterval(function () {
        $.getJSON("/get_upload_progress/" + upload_id, function (data) {
            if (data.status == "error") {

                // We got an error back so display the message and stop updating the progress bar.
                message.showMessage("error", data.message);
                clearInterval(g_progress_intv);
                g_progress_intv = 0;
                return;
            }

            if (data.length == -1) {

                percentage = "100%";
                bar.width(percentage);
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
            bar.width(percentage);
            percent.html(percentage);
        });
    }, 1000);
    return;
}
