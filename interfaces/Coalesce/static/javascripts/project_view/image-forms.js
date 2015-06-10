$(function () {

    // Widget Elements
    var progressbar = $("#image_progressbar"),
        table = $("#image_list"),
        form = $('#image-import-dialog-form'),
        placeholder =
            '<tr id="#image_placeholder"><td><p><i>This project has no image</i></p></td><td></td></tr>';

    // --- Import ---

    $(function () {

        // Local Variables
        var uploading = false;

        // Form Elements
        var image_name = $("#import_img_name"),
            disk_format = $("#import_img_disk"),
            container_format = $("#import_img_cont"),
            image_type = $("#import_img_type"),
            import_local = $("#import_local"),
            import_remote = $("#import_remote"),
            os_type = $("#os_type"),
            visibility = $("#import_img_vis"),
            image_location = "",
            allFields = $([]).add(image_name).add(disk_format).add(container_format).add(image_type).add(import_local).add(import_remote).add(image_location).add(visibility);

        $("#import-image")
            .click(function (event) {

                // Prevent scrolling to top of page on click
                event.preventDefault();

                $("#image-import-dialog-form").dialog("open");
            });

        $("#image-import-dialog-form").dialog(
            {
                autoOpen: false,
                height: 575,
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

                            disableFormInputs('image', ['text', 'select', 'file'], true);
                            disableLinks(true);

                            // Start the progress bar function so it can start querying the server for status.
                            startProgressBarUpdate(progress_id, form);

                            // All the data is good so post the data to the server.
                            image_location = import_remote;

                            var loc = image_location.val();
                            image_location = convertUrl47(image_location);
                            loc = loc.replace(/\//g, '&47');

                            var os = os_type.val();

                            url = '/import_remote/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + os + '/' + progress_id + '/';

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
                                        $('#image_list').append(newRow);

                                        // Update selects
                                        addToSelect(display_name, display_name, $("#image_name"), images);
                                        refreshSelect($("#bam-instance-image"), images);
                                        $("#bam-instance-image").append("<option></option>").val("upload").html("Upload Image");

                                        message.showMessage("success", ret_data.message);

                                        $("#image-import-dialog-form").dialog("close");
                                        disableFormInputs('image', ['text', 'select', 'file'], false);
                                        disableLinks(false);
                                        uploading = false;
                                        resetUiValidation(allFields);
                                    },
                                    error: function () {

                                        // This function is called if there was an issue posting the data to the server.
                                        message.showMessage("error", "Server Fault");

                                        $("#image-import-dialog-form").dialog("close");
                                        disableFormInputs('image', ['text', 'select', 'file'], false);
                                        disableLinks(false);
                                        uploading = false;
                                        resetUiValidation(allFields);
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
                            var url = '/import_local/' + image_name.val() + '/' + container_format.val() + '/' + disk_format.val() + '/' + image_type.val() + '/' + loc + '/' + visibility.val() + '/' + os_type.val() + '/' + progress_id + '/';

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
                                    async: true,
                                    xhr: function () {
                                        // This function will be called during the upload to update the progress of the upload.
                                        var bar = form.find('.upload-bar'),
                                            percent = form.find('.upload-percent');
                                        disableFormInputs('image', ['text', 'select', 'file'], true);

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
                                        //console.log('success: image_id:' + ret_data.image_id);
                                        $('#image_list').append(newRow);

                                        // Update selects
                                        addToSelect(display_name, display_name, $("#image_name"), images);
                                        refreshSelect($("#bam-instance-image"), images);
                                        $("#bam-instance-image").append($('<option></option>')
                                            .val("upload")
                                            .html("Upload Image"));

                                        message.showMessage("success", ret_data.message);

                                        $("#image-import-dialog-form").dialog("close");
                                        disableFormInputs('image', ['text', 'select', 'file'], false);
                                        disableLinks(false);
                                        uploading = false;
                                        resetUiValidation(allFields);
                                        resetProgressBar(form);
                                    },
                                    error: function () {

                                        // This function is called if there was an issue posting the data to the server.
                                        message.showMessage("error", "Server Fault");

                                        $("#image-import-dialog-form").dialog("close");
                                        disableFormInputs('image', ['text', 'select', 'file'], false);
                                        disableLinks(false);
                                        uploading = false;
                                        resetUiValidation(allFields);
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
    });

    // --- Delete ---

    $(function () {

        // Local Variables
        var id,
            image,
            targetRow;

        $(document).on('click', '.delete-image', function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            // Get target row element, get id from that element and use that to get the image-name-text
            targetRow = $(this).parent().parent();
            id = $(targetRow).attr("id");
            image = document.getElementById(id + "-name-text");

            // Add image-name-text to confirm-form
            $('div#image-delete-confirm-form > p > span.image-name').empty().append($(image).text());

            $('#image-delete-confirm-form').dialog("open");
        });

        $('#image-delete-confirm-form').dialog({
            autoOpen: false,
            height: 125,
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
                "Confirm": function () {

                    // Confirmed Selections
                    var confId = id,
                        confImage = $(image).text();

                    message.showMessage('notice', "Deleting " + confImage + ".");

                    // Store actions cell html
                    var actionsCell = document.getElementById(confId + "-actions-cell");
                    var actionsHtml = actionsCell.innerHTML;

                    // Disable widget view links and delete actions
                    disableLinks(true);
                    disableActions("delete-image", true);

                    // Initialize progressbar and make it visible
                    $(progressbar).progressbar({value: false});
                    disableProgressbar(progressbar, "images", false);

                    // Create loader
                    var loaderId = confId + '-loader';
                    var loaderHtml = '<div class="ajax-loader" id="' + loaderId + '"></div>';

                    // Clear clicked action link and replace with loader
                    $(actionsCell).empty().fadeOut();
                    $(actionsCell).append(loaderHtml).fadeIn();

                    $.getJSON('/delete_image/' + PROJECT_ID + '/' + confId + '/')
                        .done(function (data) {

                            if (data.status == 'error') {

                                message.showMessage('error', data.message);

                                // Restore actions cell html
                                $(actionsCell).empty().fadeOut();
                                $(actionsCell).append(actionsHtml).fadeIn();
                            }

                            if (data.status == 'success') {

                                message.showMessage('success', data.message);

                                // Remove row
                                $(targetRow).fadeOut().remove();

                                // Update selects
                                removeFromSelect(confImage, $("#image_name"), images);
                                refreshSelect($("#bam-instance-image"), images);
                                $("#bam-instance-image").append($('<option></option>')
                                    .val("upload")
                                    .html("Upload Image"));
                            }

                            // If last image, reveal placeholder
                            var rowCount = $('#image_list tr').length;
                            if (rowCount < 2) {
                                $(table).append(placeholder).fadeIn();
                            }

                        })
                        .fail(function () {

                            message.showMessage('error', 'Server Fault');

                            // Restore Actions html
                            $(actionsCell).empty().fadeOut();
                            $(actionsCell).append(actionsHtml).fadeIn();
                        })
                        .always(function () {

                            // Hide progressbar and enable widget view links
                            disableProgressbar(progressbar, "images", true);
                            disableLinks(false);
                            disableActions("delete-image", false);
                        });

                    $(this).dialog("close");
                }
            },
            close: function () {
            }
        });
    });
});