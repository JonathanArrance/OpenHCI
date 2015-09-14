var wizardSection = "initialize",
    wizardInputs = {
        "instanceName": $("#instance-name"),
        "instanceImage": $("#instance-image"),
        "instanceFlavor": $("#instance-flavor"),
        "instanceNetwork": $("#instance-network"),
        "instanceIP": $("#instance-ip"),
        "imageName": $("#image-name"),
        "imageContainer": $("#image-container"),
        "imageDisk": $("#image-disk"),
        "imageType": $("#image-type"),
        "imageLocal": $("#image-local"),
        "imageRemote": $("#image-remote"),
        "imageOS": $("#image-os"),
        "imageVisibility": $("#image-visibility"),
        "volumeExisting": $("#volume-existing"),
        "volumeName": $("#volume-name"),
        "volumeSize": $("#volume-size"),
        "volumeType": $("#volume-type"),
        "instanceKey": $("#instance-key"),
        "keyName": $("#key-name"),
        "instanceGroup": $("#instance-group"),
        "groupName": $("#group-name"),
        "groupDescription": $("#group-desc"),
        "groupTransport": $("#group-transport"),
        "groupPorts": $("#group-ports")
    };

function initializeInstanceWizard() {
    switchSections(wizardSection, "instance");
}

function changeWizardSection(button) {
    var nextSection = getNextSection(wizardSection, button);
    switchSections(wizardSection, nextSection);
}

function getNextSection(current, button) {
    var nextSection;
    switch (current) {
        case "initialize":
            nextSection = "instance";
            break;
        case "instance":
            if (button = "next") {
                if (wizardInputs.instanceImage.val() == "upload") {
                    nextSection = "image";
                } else {
                    nextSection = "volume";
                }
            }
            break;
        case "image":
            if (button == "next") {
                nextSection = "volume";
            } else if (button = "back") {
                nextSection = "instance";
            }
            break;
        case "volume":
            if (button == "next") {
                nextSection = "security"
            } else if (button == "back") {
                if (wizardInputs.instanceImage.val() == "upload") {
                    nextSection = "image";
                } else {
                    nextSection = "instance";
                }
            }
            break;
        case "security":
            if (button == "next") {
                if (wizardInputs.instanceGroup.val() == "create") {
                    nextSection = "group";
                } else {
                    nextSection = "progress";
                }
            } else if (button == "back") {
                nextSection = "volume"
            }
            break;
        case "group":
            if (button == "next") {
                nextSection = "progress"
            } else if (button == "back") {
                nextSection = "security"
            }
            break;
        case "progress":
            if (button == "back") {
                if (wizardInputs.instanceGroup.val() == "create") {
                    nextSection = "group"
                } else {
                    nextSection = "security"
                }
            }
            break;
    }
    return nextSection;
}

function switchSections(current, next) {
    if (current != "initialize") {
        var currentSection = "#wizard-" + current;
        $(currentSection).hide(0);
    }
    var nextSection = "#wizard-" + next,
        nextSection = $(nextSection),
        nextForm = "#" + next + "-form",
        nextForm = $(nextForm);
    nextSection.show(0);
    wizardSection = next;


    var createBtn = $("#wizard-create"),
        nextBtn = $("#wizard-next"),
        backBtn = $("#wizard-back"),
        finishBtn = $("#wizard-finish");

    // -- Handle Dom Manipulation
    switch (wizardSection) {
        case "instance":
            nextBtn.show(0);
            backBtn.hide(0);
            createBtn.hide(0);
            finishBtn.hide(0);
            break;
        case "image":
            backBtn.show(0);
            break;
        case "volume":
            backBtn.show(0);
            break;
        case "security":
            nextBtn.show(0);
            createBtn.hide(0);
            break;
        case "group":
            nextBtn.show(0);
            createBtn.hide(0);
            break;
        case "progress":
            updateProgressSection();
            nextBtn.hide(0);
            createBtn.show(0);
            break;
        case "confirm":
            createBtn.hide();
            backBtn.hide();
            finishBtn.show();
            break;
    }

    if (!(nextForm.valid())) {
        nextBtn.prop("disabled", "disabled");
    }

}

function updateProgressSection() {
    $(".wizard-info .instance .name").html($("#instance-name").val());
    $(".wizard-info .image .name").html(function () {
        return $("#instance-image").val() == "upload" ? $("#image-name").val() : $("#instance-image").find("option:selected").data("name");
    });
    $(".wizard-info .instance .network").html($("#instance-network").val());
    $(".wizard-info .instance .flavor").html($("#instance-flavor").val());
    $(".wizard-info .volume .name").html($("#volume-name").val());
    $(".wizard-info .volume .type").html($("#volume-type").val());
    $(".wizard-info .volume .size").html($("#volume-size").val());
    $(".wizard-info .instance .ip").html($("#instance-ip").val());
    $(".wizard-info .security .group").html(function () {
        return $("#instance-group").val() == "create" ? $("#group-name").val() : $("#instance-group").val();
    });
    $(".wizard-info .security .key").html(function () {
        return $("#instance-key").val() == "create" ? $("#key-name").val() : $("#instance-key").val();
    });
}

function buildInstance() {

    // local variables
    var uploading = false,
        uploadedImage,
        secGroup,
        secGroupDesc,
        key,
        keyId,
        instanceName,
        instanceId,
        volume,
        step = 0,
        steps = 7,
        error = false,
        page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container"),
        usersSecurity = $("#users-security-container");

    var uploadImage = $.Deferred(),
        createSecGroup = $.Deferred(),
        createKey = $.Deferred(),
        createInstance = $.Deferred(),
        createVolume = $.Deferred(),
        attachVolume = $.Deferred(),
        assignIp = $.Deferred();

    updateProgress(step, steps, "Initializing");

    if (wizardInputs.instanceImage.val() == "upload") {
        uploading = true;
        updateProgress(step, steps, "Uploading Image");
        var imageType = wizardInputs.imageType.val(),
            imageProgressId = guid(),
            url = "";
        if (imageType == "local") {
            url = '/import_local/' +
                wizardInputs.imageName.val() + '/' +
                wizardInputs.imageContainer.val() + '/' +
                wizardInputs.imageDisk.val() + '/' +
                wizardInputs.imageType.val() + '/' +
                "na" + '/' +
                wizardInputs.imageVisibility.val() + '/' +
                wizardInputs.imageOS.val() + '/' +
                imageProgressId + '/';
        } else {
            url = '/import_remote/' +
                wizardInputs.imageName.val() + '/' +
                wizardInputs.imageContainer.val() + '/' +
                wizardInputs.imageDisk.val() + '/' +
                wizardInputs.imageType.val() + '/' +
                wizardInputs.imageRemote.val() + '/' +
                wizardInputs.imageVisibility.val() + '/' +
                wizardInputs.imageOS.val() + '/' +
                imageProgressId + '/';
        }
        var formData = new FormData();
        if (imageType == "local") {
            formData.append('imageLocal', $("#image-local")[0].files[0]);
        }

        uploadImage = $.ajax({
            type: "POST",
            url: url,
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            xhr: function () {
                window.loading.add("importing");
                // This function will be called during the upload to update the progress of the upload.
                var bar = $("#wizard-image-upload-bar .progress-bar"),
                    percent = $("#wizard-image-upload-label");
                var xhr = $.ajaxSettings.xhr();
                xhr.upload.onprogress = function (e) {
                    if (e.lengthComputable) {
                        var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                        percentage = percentage + "%";
                        bar.css("width", percentage);
                        percent.html(percentage);
                    }
                };
                return xhr;
            }
        })
            .done(function (data) {
                data = JSON.parse(data);
                if (data.status == 'error') {
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, instances, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
                    $.getJSON('/projects/get/images/' + CURRENT_PROJECT_ID + '/')
                        .done(function (data) {
                            $(data).each(function (index, element) {
                                if (element.image_name == wizardInputs.imageName.val()) {
                                    uploadedImage = element.image_id;
                                }
                            });
                        });
                    step++;
                }
            })
            .fail(function () {
                showMessage("error", "Error: Could not upload image");
                error = true;
                return false;
            });
    }
    else {
        step++;
        uploadedImage = wizardInputs.instanceImage.val();
        uploadImage.resolve();
    }

    if (wizardInputs.instanceGroup.val() == "create") {
        secGroupDesc = wizardInputs.groupDescription.val() == "" ? "none" : encodeURIComponent(wizardInputs.groupDescription.val());
        updateProgress(step, steps, "Creating Group");
        createSecGroup = $.getJSON(
            '/create_security_group/' +
            wizardInputs.groupName.val() + '/' +
            secGroupDesc + '/' +
            wizardInputs.groupPorts.val() + '/' +
            wizardInputs.groupTransport.val() + '/' +
            CURRENT_PROJECT_ID + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, usersSecurity, "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
                    step++;
                    updateProgress(step, steps, "Group Created");
                    secGroup = data.sec_group_name;
                }
            }).fail(function () {
                showMessage("error", "Error: Could not create security group");
                error = true;
                return false;
            });
    } else {
        step++;
        secGroup = wizardInputs.instanceGroup.val();
        createSecGroup.resolve();
    }

    if (wizardInputs.instanceKey.val() == "create") {
        updateProgress(step, steps, "Creating Key");
        createKey = $.getJSON('/create_sec_keys/' + wizardInputs.keyName.val() + '/' + CURRENT_PROJECT_ID + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, usersSecurity, "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
                    step++;
                    updateProgress(step, steps, "Key Created");
                    key = data.key_name;
                    keyId = data.key_id;
                }
            })
            .fail(function () {
                showMessage("error", "Error: Could not create security key");
                error = true;
                return false;
            });
    } else {
        step++;
        key = wizardInputs.instanceKey.val();
        $.getJSON('/projects/get/keys/' + CURRENT_PROJECT_ID + '/')
            .done(function (data) {
                $(data).each(function (index, element) {
                    if (element.key_name == key) {
                        keyId = element.key_id;
                        createKey.resolve();
                    }
                });
            });
    }

    $.when(createSecGroup, createKey).done(function () {
        if (uploading) {
            updateProgress(step, steps, "Uploading Image");
        }
    });

    $.when(uploadImage, createSecGroup, createKey).done(function () {
        $(".wizard-confirm-key").prop("href", '/download_public_key/' + keyId + '/' + key + '/' + CURRENT_PROJECT_ID + '/');
        updateProgress(step, steps, "Creating Instance");
        createInstance = $.getJSON(
            '/create_instance/' +
            wizardInputs.instanceName.val() + '/' +
            secGroup +
            '/nova/' +
            wizardInputs.instanceFlavor.val() + '/' +
            key + '/' +
            uploadedImage + '/' +
            wizardInputs.instanceNetwork.val() + '/' +
            CURRENT_PROJECT_ID +
            '/false/none/none/none/')
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, instances, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
                    step++;
                    updateProgress(step, steps, "Instance Created");
                    $(".wizard-confirm-name").html(wizardInputs.instanceName.val());
                    instanceName = data.server_info.server_name.toString();
                    instanceId = data.server_info.server_id.toString();
                }
            })
            .fail(function () {
                showMessage("error", "Error: Could not create instance");
                error = true;
                return false;
            });

        $.when(createInstance).done(function () {
            if (wizardInputs.volumeExisting.val() == "create") {
                updateProgress(step, steps, "Creating Volume");
                createVolume = $.getJSON(
                    '/create_volume/' +
                    wizardInputs.volumeName.val() + '/' +
                    wizardInputs.volumeSize.val() + '/' +
                    wizardInputs.volumeType.val() + '/' +
                    CURRENT_PROJECT_ID + '/')
                    .done(function (data) {

                        if (data.status == 'error') {
                            showMessage('error', data.message);
                            error = true;
                            return false;
                        }

                        if (data.status == 'success') {
                            stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
                            step++;
                            updateProgress(step, steps, "Volume Created");
                            volume = data.volume_id;
                        }
                    })
                    .fail(function () {
                        showMessage("error", "Error: Could not create volume");
                        error = true;
                        return false;
                    });
            } else if (wizardInputs.volumeExisting.val() == "none") {
                volume = "skip";
                step++;
                updateProgress(step, steps, "Skipping Volume");
                createVolume.resolve();
            } else {
                volume = wizardInputs.volumeExisting.val();
                step++;
                updateProgress(step, steps, "Volume Selected");
                createVolume.resolve();
            }

            $.when(createVolume).done(function () {
                if (volume != "skip") {
                    updateProgress(step, steps, "Attaching Volume");
                    attachVolume = $.getJSON(
                        '/attach_volume/' + CURRENT_PROJECT_ID + '/' + instanceId + '/' + volume + '/')
                        .done(function (data) {

                            if (data.status == 'error') {
                                showMessage('error', data.message);
                                error = true;
                                return false;
                            }

                            if (data.status == 'success') {

                                stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
                                stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
                                step++;
                                updateProgress(step, steps, "Volume Attached");
                            }
                        })
                        .fail(function () {
                            showMessage("error", "Error: Could not attach volume");
                            error = true;
                            return false;
                        });
                } else {
                    attachVolume.resolve();
                    step++;
                }

                $.when(attachVolume).done(function () {
                    if (wizardInputs.instanceIP.val() != "none") {
                        updateProgress(step, steps, "Assigning IP");
                        assignIp = $.getJSON(
                            '/assign_floating_ip/' +
                            wizardInputs.instanceIP.val() + '/' +
                            instanceId + '/' +
                            CURRENT_PROJECT_ID + '/')
                            .done(function (data) {
                                if (data.status == 'error') {
                                    showMessage('error', data.message);
                                    error = true;
                                    return false;
                                }
                                if (data.status == 'success') {
                                    stealthRefreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
                                    stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
                                    step++;
                                    updateProgress(step, steps, "IP Assigned");
                                    $(".wizard-confirm-ip").html(wizardInputs.instanceIP.val());
                                }
                            })
                            .fail(function () {
                                showMessage("error", "Error: Could not assign ip");
                                error = true;
                                return false;
                            })
                    } else {
                        $(".wizard-confirm-ip").html("None");
                        $(".wizard-confirm-ip.example").html("204.64.2.44");
                        assignIp.resolve();
                        step++;
                    }

                    $.when(assignIp).done(function () {
                        if (!error) {
                            updateProgress(steps, steps, "Complete");
                            switchSections(wizardSection, "confirm");
                        } else {
                            updateProgress(steps, steps, "Error");
                        }
                        $("#wizard-create").removeAttr("disabled");
                        $("#wizard-back").removeAttr("disabled");
                    });
                });
            });
        });
    });
}

function updateProgress(stepCount, steps, stepLabel) {
    $("#wizard-overall-progress-bar .progress-bar").css("width", ((stepCount / steps) * 100) + "%");
    $("#wizard-overall-progress-label").html(stepLabel);
}