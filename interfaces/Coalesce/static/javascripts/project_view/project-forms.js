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
        }
    }
});

function initializeBamSection() {
    changeBamSection();
    getStorage(PROJECT_ID);
    $(".bam-overall-progress-bar").progressbar({ value: 0});
    $(".bam-image-upload-bar").progressbar({ value: 0});
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
        backBtn = $("#bam-back-button");

    // -- Handle Dom Manipulation
    switch (currentSection) {
        case "instance":
            backBtn.hide(0);
            createBtn.hide(0);
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
            nextBtn.show();
            createBtn.hide();
            break;
        case "group":
            form.dialog({height: 505});
            nextBtn.show();
            createBtn.hide();
            break;
        case "progress":
            updateProgressSection();
            form.dialog({height: 360});
            nextBtn.hide();
            createBtn.show();
            break;
        case "confirm":
            form.dialog({height: 605});
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
    if (bamParams["instance"].inputs["image"].value == "create") {
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
    console.log(bamParams);
}