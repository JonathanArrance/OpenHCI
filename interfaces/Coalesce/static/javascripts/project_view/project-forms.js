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

                    // Initialize progressbar and make it visible
                    $($("#project-delete-progressbar")).progressbar({value: false});
                    setVisible($("#project-delete-progressbar"), true);

                    $.getJSON('/projects/' + PROJECT_ID + '/' + PROJECT + '/delete/')
                        .done(function (data) {
                            if (data.status == "error") {
                                message.showMessage('error', data.message);
                                disableUiButtons('.ui-button', false);
                                setVisible($("#project-delete-progressbar"), false);
                            }
                            if (data.status == "success") {
                                message.showMessage('success', data.message);
                                location.replace('/cloud/manage');
                            }
                        })
                        .fail(function () {
                            message.showMessage('error', "Server Fault");
                            disableUiButtons('.ui-button', false);
                            setVisible($("#project-delete-progressbar"), false);
                        })
                }
            },
            close: function () {
            }
        });
    });

    // --- Project Quotas ---

    $(function () {

        // Array of updateable settings
        var settings = [
                {
                    "span": $("#project-quotas-cores").find("span"),
                    "key": "cores"
                },
                {
                    "span": $("#project-quotas-ram").find("span"),
                    "key": "ram"
                },
                {
                    "span": $("#project-quotas-instances").find("span"),
                    "key": "instances"
                },
                {
                    "span": $("#project-quotas-volumes").find("span"),
                    "key": "volumes"
                },
                {
                    "span": $("#project-quotas-gigabytes").find("span"),
                    "key": "gigabytes"
                }

            ],
            currentSettings = {};

        $("#set-quotas").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();
            $("#set-quotas").prop("disabled", true);

            $.getJSON("/projects/" + PROJECT_ID + "/get_project_quota/")
                .done(function (data) {

                    // Switch buttons
                    $("#set-quotas").hide(0);
                    $("#update-quotas").show(0);
                    $("#cancel-quotas").show(0);

                    $.each(Object.keys(data), function (i, quota) {
                        $.each(settings, function (j, setting) {
                            if (quota == setting.key) {
                                currentSettings[setting.key] = data[quota];
                                var value = $(setting.span).html();
                                $(setting.span)
                                    .empty()
                                    .append($("<input></input>")
                                        .prop("type", "text")
                                        .prop("value", value.toString())
                                        .addClass("project-quotas-input"));
                            }
                        });
                    });
                })
                .fail(function () {
                    message.showMessage('error', "Server Fault");
                })
                .always(function () {

                    $("#set-quotas").prop("disabled", false);
                });
        });

        $("#update-quotas").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            var valueString = "",
                isValid = true;

            // Disable button
            $(this).prop("disabled", true);
            $("#cancel-quotas").prop("disabled", true);

            // Disable inputs
            $.each(settings, function (index, setting) {
                $(setting.span).find("input").prop("disabled", true);
                clearUiValidation($(setting.span).find("input"));
            });

            $.each(settings, function (index, setting) {
                if (!parseInt($(setting.span).find("input").val())) {
                    isValid = false;
                    flagError($(setting.span).find("input"), "");
                    return false;
                }
            });

            if (isValid) {

                $.getJSON("/projects/" + PROJECT_ID + "/get_project_quota/")
                    .done(function (data) {
                        $.each(Object.keys(data), function (i, quota) {
                            $.each(settings, function (j, setting) {
                                if (quota == setting.key) {
                                    currentSettings[setting.key] = data[quota];
                                }
                            });
                        });
                    })
                    .fail(function () {
                        message.showMessage('error', "Server Fault");
                    });

                $.each(settings, function (index, setting) {
                    $(setting.span).attr("disabled", true);
                    valueString += setting.key + ":" + parseInt($(setting.span).find("input").val());
                    if (index + 1 != settings.length) {
                        valueString += ",";
                    }
                });

                $.getJSON("/projects/" + PROJECT_ID + "/" + valueString + "/set_project_quota/")
                    .done(function (data) {

                        if (data.status == 'error') {
                            message.showMessage('error', data.message);
                            $.each(settings, function (i, setting) {
                                $.each(Object.keys(currentSettings), function (j, current) {
                                    if (setting.key == current) {
                                        $(setting.span).empty().append(currentSettings[current])
                                    }
                                })
                            })
                        }
                        if (data.status == 'success') {
                            message.showMessage('success', data.message);
                            $.each(settings, function (i, setting) {
                                $.each(Object.keys(data.project), function (j, returned) {
                                    if (setting.key == returned) {
                                        $(setting.span).empty().append(data.project[returned]);
                                    }
                                })
                            })
                        }
                    })
                    .fail(function () {
                        message.showMessage('error', "Server Fault");
                        $.each(settings, function (i, setting) {
                            $.each(Object.keys(currentSettings), function (j, current) {
                                if (setting.key == current) {
                                    $(setting.span).empty().append(currentSettings[current])
                                }
                            })
                        })
                    })
                    .always(function () {
                        // Switch buttons
                        $("#update-quotas").prop("disabled", false).hide(0);
                        $("#cancel-quotas").prop("disabled", false).hide(0);
                        $("#set-quotas").show(0);

                        // Enable inputs
                        $.each(settings, function (index, setting) {
                            $(setting.span).find("input").prop("disabled", false);
                        });
                    });
            } else {

                // Enable button
                $("#update-quotas").prop("disabled", false);
                $("#cancel-quotas").prop("disabled", false);

                // Enable inputs
                $.each(settings, function (index, setting) {
                    $(setting.span).find("input").prop("disabled", false);
                });
            }
        });

        $("#cancel-quotas").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $.each(settings, function (i, setting) {
                $.each(Object.keys(currentSettings), function (j, current) {
                    if (setting.key == current) {
                        $(setting.span).empty().append(currentSettings[current])
                    }
                })
            });

            // Switch buttons
            $("#update-quotas").hide(0);
            $("#cancel-quotas").hide(0);
            $("#set-quotas").show(0);
        })
    });

// --- Build Instance ---

    $(function () {

        // Open modal form when build-instane button clicked
        $("#create-machine").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();
            initializeBamSection();
            $("#build-instance-form").dialog("open");
        });

        $("#bam-next-button").click(function (event) {

            event.preventDefault();
            changeBamSection("next");
        });

        $("#bam-back-button").click(function (event) {

            event.preventDefault();
            if ($(this).attr('disabled') == undefined) {
                changeBamSection("back");
            }
        });

        $("#bam-create-button").click(function (event) {

            event.preventDefault();
            if ($(this).attr('disabled') == undefined) {
                $("#bam-create-button").attr('disabled', true);
                $("#bam-back-button").attr('disabled', true);
                disableUiButtons(".ui-button", true);
                buildInstance();
            }
        });

        $("#bam-finish-button").click(function (event) {

            event.preventDefault();
            $(bamParams["confirm"].section).hide(0);
            currentSection = "initialize";
            resetBamInputs();
            $("#build-instance-form").dialog("close");

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
})
;

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
                        return checkLength(this.element, "Instance Name", standardStringMin, standardStringMax) && checkDuplicateName(this.element, instanceOpts) && checkCharfield(this.element, "Instance name");
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
                        return checkLength(this.element, "Image Name", standardStringMin, standardStringMax) && checkCharfield(this.element, "Image name");
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
                            return checkLength(this.element, "Volume Name", standardStringMin, standardStringMax) && checkDuplicateName(this.element, volumes) && checkCharfield(this.element, "Volume name");
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
                            return checkLength(this.element, "Key Pair Name", standardStringMin, standardStringMax) && checkCharfield(this.element, "Security Key name");
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
                        return checkLength(this.element, "Security Group name", standardStringMin, standardStringMax) && checkCharfield(this.element, "Security Group name");
                    },
                    "value": ""
                },
                "description": {
                    "element": $("#bam-group-description"),
                    "validation": function () {
                        return checkLength(this.element, "Security Group description", 0, 80);
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
    bamParams.group.inputs.ports.element.val("443,80,22");
    $(".bam-overall-progress-bar").progressbar({value: 0});
    $(".bam-image-upload-bar").progressbar({value: 0});
    $(".bam-overall-progress-label").html("");
    $(".bam-image-upload-label").html("");
    $("#build-instance-form").dialog("close");
}

function resetBamInputs() {
    for (var section in bamParams) {
        for (var input in bamParams[section].inputs) {
            bamParams[section].inputs[input].value = "";
            resetUiValidation(bamParams[section].inputs[input].element);
        }
    }
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
            nextBtn.show(0);
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
            form.dialog({height: 600});
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
    var uploading = false,
        uploadedImage,
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
        uploading = true;
        uploadedImage = bamParams.image.inputs.name.value;
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
                data = JSON.parse(data);
                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    addImage(data);
                    step++;
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
        uploadedImage = images.items[bamParams.instance.inputs.image.value].id;
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

    $.when(createSecGroup, createKey).done(function () {
        if (uploading) {
            updateProgress(step, steps, "Uploading Image");
        }
    });

    $.when(uploadImage, createSecGroup, createKey).done(function () {
        $(".bam-confirm-key").prop("href", '/download_public_key/' + keyId + '/' + key + '/' + PROJECT_ID + '/');
        updateProgress(step, steps, "Creating Instance");
        createInstance = $.getJSON(
            '/create_instance/' +
            bamParams.instance.inputs.name.value + '/' +
            secGroup +
            '/nova/' +
            flavors.items[bamParams.instance.inputs.flavor.value].id + '/' +
            key + '/' +
            uploadedImage + '/' +
            bamParams.instance.inputs.network.value + '/' +
            PROJECT_ID + '/false/none/none/none/')
            .done(function (data) {
                if (data.status == 'error') {
                    message.showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
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
                                snapshotVolumes.removeItem(volume);
                                refreshSelect($("#snap_volume"), snapshotVolumes);
                                refreshSelect("#bam-volume-select-existing", snapshotVolumes);
                                $('<option></option>')
                                    .val("none")
                                    .html("Skip Adding Storage")
                                    .prop("selected", "selected")
                                    .prependTo($("#bam-volume-select-existing"));
                                $('<option></option>')
                                    .val("create")
                                    .html("Create Volume")
                                    .appendTo($("#bam-volume-select-existing"));
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
                                    addIp(data, instanceId);
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
                        $("#bam-create-button").removeAttr("disabled");
                        $("#bam-back-button").removeAttr("disabled");
                        disableUiButtons(".ui-button", false);
                    });
                });
            });
        });
    });
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
        .appendTo($('#image_list').fadeIn());
    // Update selects
    addToSelect(bamParams.image.inputs.name.value, bamParams.image.inputs.name.value, $("#image_name"), images);
    refreshSelect($("#bam-instance-image"), images);
    $("#bam-instance-image").append($('<option></option>')
        .val("upload")
        .html("Upload Image"));
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
    refreshSelect($("#bam-security-group"), secGroupInstOpts);
    $("#bam-security-group").append($('<option></option>')
        .val("create")
        .html("Create Group"));
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

    var rowCount = $("#keypair_list tr").length;
    if (rowCount >= 2) {
        $("#keypair_placeholder").remove().fadeOut();
    }

    addToSelect(data.key_name, data.key_name, $("#sec_key_name"), secKeyInstOpts);
    refreshSelect($("#bam-security-select-key"), secKeyInstOpts);
    $("#bam-security-select-key").append($('<option></option>')
        .val("create")
        .html("Create Key"));
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

    volumes.setItem(data.volume_id, {size: data.volume_size, name: data.volume_name});
    snapshotVolumes.setItem(data.volume_id, {
        value: data.volume_id,
        option: data.volume_name
    });

    refreshSelect($("#snap_volume"), snapshotVolumes);
    refreshSelect("#bam-volume-select-existing", snapshotVolumes);
    $('<option></option>')
        .val("none")
        .html("Skip Adding Storage")
        .prop("selected", "selected")
        .prependTo($("#bam-volume-select-existing"));
    $('<option></option>')
        .val("create")
        .html("Create Volume")
        .appendTo($("#bam-volume-select-existing"));
}

function addIp(data, instanceId) {

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
    refreshSelect($("#bam-security-ip"), assignableFips);
    $('<option></option>')
        .val("none")
        .html("Skip Attaching IP")
        .prop("selected", "selected")
        .prependTo($("#bam-security-ip"));
    removeFromSelect(instanceId, instanceId, assignableInstances);

    // Add assigned class
    $(document.getElementById(data.floating_ip_id)).addClass("fip-assigned");
}
