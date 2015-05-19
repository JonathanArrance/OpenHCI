$(function () {

    // --- Delete ---

    $(function () {

        // Open modal form when delete-project button clicked
        $("#delete-project").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#project-delete-confirm-form").dialog("open");
        });

        $("#project-delete-confirm-form").dialog({
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

                    message.showMessage('notice', "Deleting Project");

                    disableUiButtons('.ui-button', true);

                    $.getJSON('/projects/' + PROJECT_ID + '/' + PROJECT + '/delete/')
                        .done(function (data) {
                            if (data.status == "error") {
                                message.showMessage('error', data.message);
                                disableUiButtons('.ui-button', false);
                            }
                            if (data.status == "success") {
                                message.showMessage('success', data.message);
                                location.replace('/cloud/manage');
                            }
                        })
                        .fail(function () {
                            disableUiButtons('.ui-button', false);
                        })
                }
            },
            close: function () {
            }
        });
    });

    // --- Build Instance ---

    $(function () {

        // Open modal form when delete-project button clicked
        $("#create-machine").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            if (currentSection == "initialize") {
                initializeBamSection();
            }
            $("#build-instance-form").dialog("open");
        });

        $("#bam-next-button").click(function (event) {

            event.preventDefault();
            changeBamSection("next");
        });

        $("#bam-back-button").click(function (event) {

            event.preventDefault();
            changeBamSection("back");
        });

        $("#bam-create-button").click(function (event) {

            event.preventDefault();
            buildInstance();
        });

        $("#bam-image-location").change(function () {
            changeImageLocation($(this), $("#bam-image-import-local"), $("#bam-image-import-remote"));
        });

        changeImageLocation($("#bam-image-location"), $("#bam-image-import-local"), $("#bam-image-import-remote"));

        $("#build-instance-form").dialog({
            autoOpen: false,
            height: 455,
            width: 600,
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
            close: function () {
            }
        });
    });
});

// Declare and Initialize variables on document ready
var currentSection,
    bamParams;

$(function () {
    currentSection = "initialize";
    bamParams = {
        "instance": {
            "section": "#bam-instance-section",
            "inputs": {
                "name": {
                    "element": $("#bam-instance-name"),
                    "validation": function () {
                        return checkLength(this.element, "Instance Name", 3, 16) && checkDuplicateName(this.element, instanceOpts);
                    },
                    "value": ""
                },
                "image": {
                    "element": $("#bam-instance-image"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "network": {
                    "element": $("#bam-instance-network"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "flavor": {
                    "element": $("#bam-instance-flavor"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                }
            }
        },
        "image": {
            "section": "#bam-image-section",
            "inputs": {
                "name": {
                    "element": $("#bam-image-name"),
                    "validation": function () {
                        return checkLength(this.element, "Image Name", 3, 20);
                    },
                    "value": ""
                },
                "container": {
                    "element": $("#bam-image-container"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "disk": {
                    "element": $("#bam-image-disk"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "type": {
                    "element": $("#bam-image-location"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "importLocal": {
                    "element": $("#bam-image-import-local"),
                    "validation": function () {
                        if ($("#bam-image-location").val() == "image_file") {
                            return checkFile(this.element);
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "importRemote": {
                    "element": $("#bam-image-import-remote"),
                    "validation": function () {
                        if ($("#bam-image-location").val() == "image_url") {
                            return checkUrl(this.element);
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "os": {
                    "element": $("#bam-image-os"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "visibility": {
                    "element": $("#bam-image-visibility"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                }
            }
        },
        "volume": {
            "section": "#bam-volume-section",
            "inputs": {
                "select": {
                    "element": $("#bam-volume-select-existing"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "name": {
                    "element": $("#bam-volume-name"),
                    "validation": function () {
                        if ($("#bam-volume-select-existing").val() == "create") {
                            return checkLength(this.element, "Volume Name", 3, 16) && checkDuplicateName(this.element, volumes);
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "size": {
                    "element": $("#bam-volume-size"),
                    "validation": function () {
                        if ($("#bam-volume-select-existing").val() == "create") {
                            return checkSize(this.element, "Volume Size must be greater than 0.", 1, 0) && checkStorage(this.element);
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "type": {
                    "element": $("#bam-volume-type"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                }
            }
        },
        "security": {
            "section": "#bam-security-section",
            "inputs": {
                "ip": {
                    "element": $("#bam-security-ip"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "key": {
                    "element": $("#bam-security-select-key"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "newKey": {
                    "element": $("#bam-security-create-key"),
                    "validation": function () {
                        if ($("#bam-security-select-key").val() == "create") {
                            return checkLength(this.element, "Key Pair Name", 3, 16);
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "group": {
                    "element": $("#bam-security-group"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                }
            }
        },
        "group": {
            "section": "#bam-group-section",
            "inputs": {
                "name": {
                    "element": $("#bam-group-name"),
                    "validation": function () {
                        return checkLength(this.element, "Security Group Name", 3, 16);
                    },
                    "value": ""
                },
                "description": {
                    "element": $("#bam-group-description"),
                    "validation": function () {
                        return checkLength(this.element, "Security Group Description", 0, 80);
                    },
                    "value": ""
                },
                "transport": {
                    "element": $("#bam-group-transport"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "ports": {
                    "element": $("#bam-group-ports"),
                    "validation": function () {
                        if (this["value"] == "") {
                            this["value"] = "443,80,22";
                        }
                        return true;
                    },
                    "value": ""
                }
            }
        },
        "progress": {
            "section": "#bam-progress-section"
        },
        "confirm": {
            "section": "#bam-confirm-section"
        }
    }
});

function initializeBamSection() {
    changeBamSection();
    getStorage(PROJECT_ID);
    $(".bam-overall-progress-bar").progressbar({value: 0});
    $(".bam-image-upload-bar").progressbar({value: 0});
    $("#build-instance-form").dialog("close");
}

function changeBamSection(button) {

    for (var section in bamParams) {
        for (var input in bamParams[section].inputs) {
            clearUiValidation(bamParams[section].inputs[input].element);
        }
    }

    // Handle Inputs
    var nextSection = getNextSection(currentSection, button);
    switchSections(currentSection, nextSection);
}

function getNextSection(current, button) {
    var nextSection;
    switch (current) {
        case "initialize":
            nextSection = "instance";
            break;
        case "instance":
            if (button = "next") {
                if (getInputs(current)) {
                    if (bamParams.instance.inputs.image.value == "upload") {
                        nextSection = "image";
                    } else {
                        nextSection = "volume";
                    }
                } else {
                    nextSection = current;
                }
            }
            break;
        case "image":
            if (button == "next") {
                if (getInputs(current)) {
                    nextSection = "volume";
                } else {
                    nextSection = current;
                }
            } else if (button = "back") {
                nextSection = "instance";
            }
            break;
        case "volume":
            if (button == "next") {
                if (getInputs(current)) {
                    nextSection = "security"
                } else {
                    nextSection = current;
                }
            } else if (button == "back") {
                if (bamParams.instance.inputs.image.value == "upload") {
                    nextSection = "image";
                } else {
                    nextSection = "instance";
                }
            }
            break;
        case "security":
            if (button == "next") {
                if (getInputs(current)) {
                    if (bamParams[current].inputs.group.value == "create") {
                        nextSection = "group";
                    } else {
                        nextSection = "progress";
                    }
                } else {
                    nextSection = current;
                }
            } else if (button == "back") {
                nextSection = "volume"
            }
            break;
        case "group":
            if (button == "next") {
                if (getInputs(current)) {
                    nextSection = "progress"
                } else {
                    nextSection = current;
                }
            } else if (button == "back") {
                nextSection = "security"
            }
            break;
        case "progress":
            if (button == "back") {
                if (bamParams["security"].inputs.group.value == "create") {
                    nextSection = "group"
                } else {
                    nextSection = "security"
                }
            }
            break;
    }
    return nextSection;
}

function getInputs(section) {
    for (var key in bamParams[section].inputs) {
        if (bamParams[section].inputs[key].validation()) {
            bamParams[section].inputs[key].value = bamParams[section].inputs[key].element.val();
        } else {
            return false;
        }
    }
    return true;
}

function switchSections(current, next) {
    if (current != "initialize") {
        $(bamParams[current].section).hide(0);
    }
    $(bamParams[next].section).show(0);
    currentSection = next;

    var form = $("#build-instance-form"),
        createBtn = $("#bam-create-button"),
        nextBtn = $("#bam-next-button"),
        backBtn = $("#bam-back-button"),
        finishBtn = $("#bam-finish-button");

    // -- Handle Dom Manipulation
    switch (currentSection) {
        case "instance":
            backBtn.hide(0);
            createBtn.hide(0);
            finishBtn.hide(0);
            form.dialog({height: 455});
            break;
        case "image":
            backBtn.show(0);
            form.dialog({height: 610});
            changeImageLocation($("#bam-image-location"), $("bam-image-import-local"), $("bam-image-import-remote"));
            break;
        case "volume":
            backBtn.show(0);
            form.dialog({height: 560});
            break;
        case "security":
            form.dialog({height: 605});
            nextBtn.show(0);
            createBtn.hide(0);
            break;
        case "group":
            form.dialog({height: 505});
            nextBtn.show(0);
            createBtn.hide(0);
            break;
        case "progress":
            updateProgressSection();
            form.dialog({height: 445});
            nextBtn.hide(0);
            createBtn.show(0);
            break;
        case "confirm":
            createBtn.hide();
            backBtn.hide();
            finishBtn.show();
            form.dialog({height: 610});
            break;
    }
}

function updateProgressSection() {
    $("#bam-progress-section").find("div.bam-form").find("ul").children().each(function () {
        if ($(this).attr("class") != undefined) {

            $(this).find("span").html(bamParams[$(this).attr("class")].inputs[$(this).find("span").attr("class")].value);

            if ($(this).attr("class") == "image") {
                checkImageInput(this);
            } else if ($(this).attr("class") == "volume") {
                checkVolumeInputs(this);
            } else if ($(this).attr("class") == "security") {
                checkSecurityInputs(this);
            }
        }
    });
}

function checkImageInput(self) {
    if (bamParams["instance"].inputs["image"].value == "upload") {
        $(self).find("span").html(bamParams["image"].inputs["name"].value);
    } else {
        $(self).find("span").html(bamParams["instance"].inputs["image"].value);
    }
}

function checkVolumeInputs(self) {
    if (bamParams["volume"].inputs["select"].value == "none") {
        if ($(self).find("span").attr("class") == "name") {
            $(self).find("span").html("Skip");
        } else if ($(self).find("span").attr("class") == "size") {
            $(self).find("span").html("N/A");
        } else if ($(self).find("span").attr("class") == "type") {
            $(self).find("span").html("N/A");
        }
    } else if (bamParams["volume"].inputs["select"].value != "none" && bamParams["volume"].inputs["select"].value != "create") {
        if ($(self).find("span").attr("class") == "name") {
            $(self).find("span").html(volumes.getItem(bamParams["volume"].inputs["select"].value).name);
        } else if ($(self).find("span").attr("class") == "size") {
            $(self).find("span").html(volumes.getItem(bamParams["volume"].inputs["select"].value).size);
        } else if ($(self).find("span").attr("class") == "type") {
            $(self).find("span").html(volumes.getItem(bamParams["volume"].inputs["select"].value).type);
        }
    }
}

function checkSecurityInputs(self) {
    if ($(self).find("span").attr("class") == "ip") {
        if (bamParams["security"].inputs["ip"].value == "none") {
            $(self).find("span").html("Skip");
        } else {
            $(self).find("span").html(assignableFips.getItem(bamParams["security"].inputs["ip"].value).option)
        }
    } else if ($(self).find("span").attr("class") == "group") {
        if (bamParams["security"].inputs["group"].value == "create") {
            $(self).find("span").html(bamParams["group"].inputs["name"].value);
        }
    } else if ($(self).find("span").attr("class") == "key") {
        if (bamParams["security"].inputs["key"].value == "create") {
            $(self).find("span").html(bamParams["security"].inputs["newKey"].value);
        }
    }
}

function buildInstance() {

    // local variables
    var uploadedImage,
        secGroup,
        key,
        keyId,
        instanceName,
        instanceId,
        volume,
        step = 0,
        steps = 7,
        error = false;

    var uploadImage = $.Deferred(),
        createSecGroup = $.Deferred(),
        createKey = $.Deferred(),
        createInstance = $.Deferred(),
        createVolume = $.Deferred(),
        attachVolume = $.Deferred(),
        assignIp = $.Deferred();

    updateProgress(step, steps, "Initializing");

    if (bamParams.instance.inputs.image.value == "upload") {
        updateProgress(step, steps, "Uploading Image");
        var imageType = bamParams.image.inputs.type.value,
            imageProgressId = guid(),
            url = "";
        if (imageType == "image_file") {
            url = '/import_local/' +
            bamParams.image.inputs.name.value + '/' +
            bamParams.image.inputs.container.value + '/' +
            bamParams.image.inputs.disk.value + '/' +
            bamParams.image.inputs.type.value + '/' +
            "na" + '/' +
            bamParams.image.inputs.visibility.value + '/' +
            bamParams.image.inputs.os.value + '/' +
            imageProgressId + '/';
        } else {
            url = '/import_remote/' +
            bamParams.image.inputs.name.value + '/' +
            bamParams.image.inputs.container.value + '/' +
            bamParams.image.inputs.disk.value + '/' +
            bamParams.image.inputs.type.value + '/' +
            bamParams.image.inputs.importRemote.value + '/' +
            bamParams.image.inputs.visibility.value + '/' +
            bamParams.image.inputs.os.value + '/' +
            imageProgressId + '/';
        }

        uploadImage = $.ajax({
            type: "POST",
            url: url,
            data: new FormData($("#bam-image-section")[0]),
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            xhr: function () {
                // This function will be called during the upload to update the progress of the upload.
                var xhr = $.ajaxSettings.xhr();
                $(".bam-image-upload-bar").progressbar({value: 0});
                xhr.upload.onprogress = function (e) {
                    if (e.lengthComputable) {
                        var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                        $(".bam-image-upload-bar").progressbar({value: percentage});
                        percentage = percentage + "%";
                        $('.bam-image-upload-label').html(percentage);
                    }
                };
                return xhr;
            }
        })
            .done(function (data) {
                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    addImage(data);
                    step++;
                    uploadedImage = bamParams.image.inputs.name.value;
                }
            })
            .fail(function () {
                message.showMessage("error", "Error: Could not upload image");
                error = true;
                return false;
            });
    }
    else {
        step++;
        uploadedImage = bamParams.instance.inputs.image.value;
        uploadImage.resolve();
    }

    if (bamParams.security.inputs.group.value == "create") {

        updateProgress(step, steps, "Creating Group");
        createSecGroup = $.getJSON(
            '/create_security_group/' +
            bamParams.group.inputs.name.value + '/' +
            bamParams.group.inputs.description.value + '/' +
            bamParams.group.inputs.ports.value + '/' +
            bamParams.group.inputs.transport.value + '/' +
            PROJECT_ID + '/')
            .done(function (data) {

                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    // Initialize empty string for new router row
                    addSecGroup(data);
                    step++;
                    updateProgress(step, steps, "Group Created");
                    secGroup = bamParams["group"].inputs["name"].value;
                }
            }).fail(function () {
                message.showMessage("error", "Error: Could not create security group");
                error = true;
                return false;
            });
    } else {
        step++;
        secGroup = bamParams.security.inputs.group.value;
        createSecGroup.resolve();
    }

    if (bamParams.security.inputs.key.value == "create") {
        updateProgress(step, steps, "Creating Key");
        createKey = $.getJSON('/create_sec_keys/' + bamParams.security.inputs.newKey.value + '/' + PROJECT_ID + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    // Initialize empty string for new router row
                    addKey(data);
                    step++;
                    updateProgress(step, steps, "Key Created");
                    key = data.key_name;
                    keyId = data.key_id;
                }
            })
            .fail(function () {
                message.showMessage("error", "Error: Could not create security key");
                error = true;
                return false;
            });
    } else {
        step++;
        key = bamParams.security.inputs.key.value;
        keyId = secKeyInstOpts.items[key].id;
        createKey.resolve();
    }

    $.when(uploadImage, createSecGroup, createKey)
        .done(function () {
            $(".bam-confirm-key").prop("href", '/download_public_key/' + keyId + '/' + key + '/' + PROJECT_ID + '/');
            updateProgress(step, steps, "Creating Instance");
            createInstance = $.getJSON(
                '/create_image/' +
                bamParams.instance.inputs.name.value + '/' +
                secGroup +
                '/nova/' +
                bamParams.instance.inputs.flavor.value + '/' +
                key + '/' +
                uploadedImage + '/' +
                bamParams.instance.inputs.network.value + '/' +
                PROJECT_ID + '/')
                .done(function (data) {
                    if (data.status == 'error') {
                        message.showMessage('error', data.message);
                        error = true;
                        return false;
                    }
                    if (data.status == 'success') {
                        // Initialize empty string for new router row
                        addInstance(data);
                        step++;
                        updateProgress(step, steps, "Instance Created");
                        $(".bam-confirm-name").html(bamParams.instance.inputs.name.value.toString());
                        instanceName = data.server_info.server_name.toString();
                        instanceId = data.server_info.server_id.toString();
                    }
                })
                .fail(function () {
                    message.showMessage("error", "Error: Could not create instance");
                    error = true;
                    return false;
                });

            $.when(createInstance).done(function () {
                if (bamParams.volume.inputs.select.value == "create") {
                    updateProgress(step, steps, "Creating Volume");
                    createVolume = $.getJSON(
                        '/create_volume/' +
                        bamParams.volume.inputs.name.value + '/' +
                        bamParams.volume.inputs.size.value + '/' +
                        bamParams.volume.inputs.type.value + '/' +
                        PROJECT_ID + '/')
                        .done(function (data) {

                            if (data.status == 'error') {
                                message.showMessage('error', data.message);
                                error = true;
                                return false;
                            }

                            if (data.status == 'success') {
                                addVolume(data, instanceName);
                                step++;
                                updateProgress(step, steps, "Volume Created");
                                volume = data.volume_id.toString();
                            }
                        })
                        .fail(function () {
                            message.showMessage("error", "Error: Could not create volume");
                            error = true;
                            return false;
                        });
                } else if (bamParams.volume.inputs.select.value == "none") {
                    volume = "skip";
                    step++;
                    updateProgress(step, steps, "Skipping Volume");
                    createVolume.resolve();
                } else {
                    volume = bamParams.volume.inputs.select.value;
                    step++;
                    updateProgress(step, steps, "Volume Selected");
                    createVolume.resolve();
                }

                $.when(createVolume).done(function () {
                    if (volume != "skip") {
                        updateProgress(step, steps, "Attaching Volume");
                        attachVolume = $.getJSON(
                            '/attach_volume/' + PROJECT_ID + '/' + instanceId + '/' + volume + '/')
                            .done(function (data) {

                                if (data.status == 'error') {
                                    message.showMessage('error', data.message);
                                    error = true;
                                    return false;
                                }

                                if (data.status == 'success') {

                                    var volumeRowSelector = "#" + volume;
                                    step++;
                                    updateProgress(step, steps, "Volume Attached");
                                    $(volumeRowSelector).addClass("volume-attached");
                                }
                            })
                            .fail(function () {
                                message.showMessage("error", "Error: Could not attach volume");
                                error = true;
                                return false;
                            });
                    } else {
                        attachVolume.resolve();
                        step++;
                    }

                    $.when(attachVolume).done(function () {
                        if (bamParams.security.inputs.ip.value != "none") {
                            updateProgress(step, steps, "Assigning IP");
                            assignIp = $.getJSON(
                                '/assign_floating_ip/' +
                                assignableFips.getItem(bamParams["security"].inputs["ip"].value).option + '/' +
                                instanceId + '/' +
                                PROJECT_ID + '/')
                                .done(function (data) {

                                    if (data.status == 'error') {
                                        message.showMessage('error', data.message);
                                        error = true;
                                        return false;
                                    }

                                    if (data.status == 'success') {
                                        addIp(data, instanceId, instanceName);
                                        step++;
                                        updateProgress(step, steps, "IP Assigned");
                                        $(".bam-confirm-ip").html(fips.getItem(bamParams["security"].inputs["ip"].value).ip);
                                    }
                                })
                                .fail(function () {
                                    message.showMessage("error", "Error: Could not assign ip");
                                    error = true;
                                    return false;
                                })
                        } else {
                            assignIp.resolve();
                            step++;
                        }

                        $.when(assignIp).done(function () {
                            if (!error) {
                                updateProgress(steps, steps, "Complete");
                                switchSections(currentSection, "confirm");
                            } else {
                                updateProgress(steps, steps, "Error");
                            }
                        });
                    });
                });
            });
        }
    )
    ;
}

function updateProgress(stepCount, steps, stepLabel) {
    $(".bam-overall-progress-bar").progressbar({value: (stepCount / steps) * 100});
    $(".bam-overall-progress-label").html(stepLabel);
}

function addImage(data) {
    $("<tr></tr>")
        .prop("id", data.image_id)
        .append($("<td></td>")
            .prop("id", data.image_id + '-name-cell')
            .append($("<span></span>")
                .prop("id", data.image_id + '-name-text')
                .html(bamParams.image.inputs.name.value.toString())))
        .append($("<td></td>")
            .prop("id", data.image_id + "-actions-cell")
            .append(
            $("<a></a>")
                .prop("href", "#")
                .prop("class", "delete-image")
                .html("delete")))
        .appendTo($('#image_list'));
    // Update selects
    addToSelect(bamParams.image.inputs.name.value, bamParams.image.inputs.name.value, $("#image_name"), imageInstOpts);
    refreshSelect($("#bam-instance-image"), imageInstOpts);
}

function addSecGroup(data) {

    $("<tr></tr>")
        .prop("id", data.sec_group_id)
        .append($("<td></td>")
            .prop("id", data.sec_group_id + '-name-cell')
            .append($("<a></a>")
                .prop("href", '/security_group/' + data.sec_group_id + '/' + PROJECT_ID + '/view/')
                .append($("<span></span>")
                    .prop("id", data.sec_group_id + '-name-text')
                    .html(data.sec_group_name.toString()))))
        .append($("<td></td>")
            .prop("id", data.sec_group_id + '-username-cell')
            .append($("<span></span>")
                .prop("id", data.sec_group_id + '-username-text')
                .html(data.username.toString())))
        .append($("<td></td>")
            .prop("id", data.sec_group_id + '-actions-cell')
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", "delete-secGroup")
                .html("delete")))
        .appendTo($("#secGroup_list")).fadeIn();

    // Check to see if this is the first sec group to be generated
    var rowCount = $("#secGroup_list tr").length;
    if (rowCount >= 2) {
        $("#secGroup_placeholder").remove().fadeOut();
    }

    // Update selects
    addToSelect(data.sec_group_name, data.sec_group_name, $("#sec_group_name"), secGroupInstOpts);
    refreshSelect($("#bam-security-group"), secGroupInstOpts)
}

function addKey(data) {
    $("<tr></tr>")
        .prop("id", data.key_id)
        .append($("<td></td>")
            .prop("id", data.key_id + '-name-cell')
            .append($("<a></a>")
                .prop("href", '/key_pair/' + data.key_id + '/' + PROJECT_ID + '/view/')
                .append($("<span></span>")
                    .prop("id", data.key_id + '-name-text')
                    .html(data.key_name.toString()))))
        .append($("<td></td>")
            .prop("id", data.key_id + '-user-cell')
            .append($("<span></span>")
                .prop("id", data.key_id + '-user-text')
                .html(USERNAME.toString())))
        .append($("<td></td>")
            .prop("id", data.key_id + '-actions-cell')
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", "delete-keypair")
                .html("delete")))
        .appendTo($("#keypair_list")).fadeIn();

    // Check to see if this is the first router to be generated, if so remove placeholder and reveal delete-router button
    var rowCount = $("#keypair_list tr").length;
    if (rowCount >= 2) {
        $("#keypair_placeholder").remove().fadeOut();
    }

    // Update Selects
    addToSelect(data.key_name, data.key_name, $("#sec_key_name"), secKeyInstOpts);
    refreshSelect($("#bam-security-select-key"), secKeyInstOpts);
}

function addInstance(data) {
    $("<tr></tr>")
        .prop("id", data.server_info.server_id)
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-name-cell')
            .append($("<a></a>")
                .prop("href", '/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/')
                .append($("<span></span>")
                    .prop("id", data.server_info.server_id + '-name-text')
                    .html(data.server_info.server_name.toString()))))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-status-cell')
            .html("ACTIVE"))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-os-cell')
            .html(data.server_info.server_os.toString() + ' / ' + data.server_info.server_flavor.toString()))
        .append($("<td></td>")
            .prop("id", data.server_info.server_id + '-actions-cell')
            .append($("<a></a>")
                .prop("href", data.server_info.novnc_console)
                .prop("class", "open-instance-console")
                .on("click", function () {
                    window.open(this.href, "_blank", "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                })
                .html("console"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'pause-instance ' + data.server_info.server_id + '-disable-action')
                .html("pause"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'suspend-instance ' + data.server_info.server_id + '-disable-action')
                .html("suspend"))
            .append($("<span></span>")
                .prop("class", "instance-actions-pipe")
                .html(" | "))
            .append($("<a></a>")
                .prop("href", "#")
                .prop("class", 'delete-instance ' + data.server_info.server_id + '-disable-action')
                .html("delete"))
    ).appendTo($("#instance_list")).fadeIn();

    // Check table length, remove placeholder if necessary
    var rowCount = $('#instance_list tr').length;
    if (rowCount >= 2) {
        $('#instance_placeholder').remove().fadeOut();
        setVisible("#create-instance-snapshot", true);
    }

    // Add to instances
    instances.setItem(
        data.server_info.server_id,
        {
            id: data.server_info.server_id,
            name: data.server_info.server_name,
            status: data.server_info.server_status,
            flavor: data.server_info.server_flavor,
            os: data.server_info.server_os,
            console: data.server_info.novnc_console
        }
    );
    consoleLinks.setItem(
        data.server_info.server_id,
        {
            link: data.server_info.novnc_console,
            html: '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>'
        }
    );

    // Update selects
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance"), attachableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#assign_instance"), assignableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance_to_snap"), instanceOpts);
}

function addVolume(data, instanceName) {
    $("<tr></tr>")
        .prop("id", data.volume_id.toString())
        .prop("class", data.volume_size.toString())
        .append(
        $("<td></td>")
            .prop("id", data.volume_id + '-name-cell')
            .append(
            $("<a></a>")
                .prop("href", '/projects/' + PROJECT_ID + '/volumes/' + data.volume_id + '/view/')
                .append(
                $("<span></span>")
                    .prop("id", data.volume_id + '-name-text')
                    .html(data.volume_name.toString()))))
        .append(
        $("<td></td>")
            .prop("id", data.volume_id + '-attached-cell')
            .append(
            $("<span></span>")
                .html(instanceName)))
        .append(
        $("<td></td>")
            .prop("id", data.volume_id + '-actions-cell')
            .append(
            $("<a></a>")
                .prop("href", "#")
                .prop("class", "detach-volume")
                .html("detach"))
            .append(
            $("<span></span>")
                .prop("class", "volume-actions-pipe")
                .html(" | "))
            .append(
            $("<a></a>")
                .prop("href", "#")
                .prop("class", "clone-volume")
                .html("clone"))
            .append(
            $("<span></span>")
                .prop("class", "volume-actions-pipe")
                .html(" | "))
            .append(
            $("<a></a>")
                .prop("href", "#")
                .prop("class", "revert-volume")
                .html("revert")))
        .appendTo($("#volume_list")).fadeIn();

    // Check to see if this is the first volume to be generated, if so remove placeholder and reveal create-snapshot buttons
    var rowCount = $("#volume_list tr").length;
    if (rowCount >= 2) {
        $("#volume_placeholder").remove().fadeOut();
        setVisible('#create-snapshot', true);
    }

    // Add to volumes
    volumes.setItem(data.volume_id, {
        size: data.volume_size,
        name: data.volume_name
    });

    // Update usedStorage
    updateUsedStorage();
    updateStorageBar();
}

function addIp(data, instanceId, instanceName) {

    // Update instance and action cells
    var instanceCell = document.getElementById(data.floating_ip_id + "-instance-cell");
    var actionsCell = document.getElementById(data.floating_ip_id + "-actions-cell");
    var instanceHtml = '<span id="' + data.floating_ip_id + '-instance-name">' + data.instance_name + '</span>';
    var newAction = '<a href="#" id="' + data.floating_ip_id + '" class="unassign_ip">unassign</a>';

    $(instanceCell).empty().fadeOut();
    $(actionsCell).empty().fadeOut();

    $(instanceCell).append(instanceHtml).fadeIn();
    $(actionsCell).append(newAction).fadeIn();

    // Update assign_ip selects
    removeFromSelect(data.floating_ip_id, data.floating_ip, assignableFips);
    refreshSelect($("#bam-security-fip"), assignableFips);
    removeFromSelect(instanceId, instanceName, assignableInstances);

    // Add assigned class
    $(document.getElementById(data.floating_ip_id)).addClass("fip-assigned");
}
