$(function () {
    // Declare Page Container
    var page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container"),
        usersSecurity = $("#users-security-container");

    // --- Sidebar Nav ---
    $("#project").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
        window.loading.current = project;
    });

    $("#instances").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, instances, [], "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
        window.loading.current = instances;
    });

    $("#storage").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, storage, [], "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
        window.loading.current = storage;
    });

    $("#networking").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, networking, [], "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
        window.loading.current = networking;
    });

    $("#users-security").click(function (event) {
        event.preventDefault();
        switchPageContent($(this), page, window.loading.current, usersSecurity, [], "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
        window.loading.current = usersSecurity;
    });

    // --- Click Events ---

    // Project
    $(document).on('click', '#delete-project', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("redirect-to:/cloud/manage/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Instances
    $(document).on('click', '.instance-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '#create-instance', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/instance/get/create/' + CURRENT_PROJECT_ID + '/');
    });

    $(document).on('click', '.delete-instance, .pause-instance, .unpause-instance, .suspend-instance, .resume-instance, .power-on-instance, .power-off-instance, .power-cycle-instance, .reboot-instance', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Images
    $(document).on('click', '.import-image', function (event) {
        event.preventDefault();
        showLoader(page);
        showConfirmModal('/image/get/import/');
    });

    $(document).on('click', '.delete-image', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Storage
    $(document).on('click', '.volume-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '.create-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/create/' + CURRENT_PROJECT_ID + '/');
    });

    $(document).on('click', '.attach-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/attach/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.revert-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/revert/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.clone-volume', function (event) {
        event.preventDefault();
        showConfirmModal('/volume/get/clone/' + CURRENT_PROJECT_ID + '/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.create-snapshot', function (event) {
        event.preventDefault();
        showConfirmModal('/snapshot/get/create/' + $(this).data("volume") + '/');
    });

    $(document).on('click', '.create-volume-from-snapshot', function (event) {
        event.preventDefault();
        showConfirmModal('/snapshot/get/create_volume/' + CURRENT_PROJECT_ID + '/' + $(this).data("snapshot") + '/');
    });

    $(document).on('click', '.detach-volume, .delete-volume, .delete-snapshot', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Networking
    $(document).on('click', '.network-name button, .router-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', "#allocate-ip", function (event) {
        event.preventDefault();
        showMessage('info', "Allocating IP.");

        $.getJSON('/allocate_floating_ip/' + CURRENT_PROJECT_ID + '/' + DEFAULT_PUBLIC + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    showMessage('success', "Successfully allocated " + data.ip_info.floating_ip + ".");
                    refreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
                }
            })
            .fail(function () {
                showMessage('error', 'Server Fault');
            })
    });

    $(document).on('click', '.assign-ip', function (event) {
        event.preventDefault();
        showConfirmModal('/floating_ip/get/assign/' + CURRENT_PROJECT_ID + '/' + $(this).data("ip") + '/');
    });

    $(document).on('click', ".deallocate-ip, .delete-network, .delete-router", function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    $(document).on('click', '.create-network', function (event) {
        event.preventDefault();
        showConfirmModal('/network/get/create/');
    });

    $(document).on('click', '.create-router', function (event) {
        event.preventDefault();
        showConfirmModal('/router/get/create/' + CURRENT_PROJECT_ID + "/");
    });

    // Users/Security
    $(document).on('click', '.user-name button, .group-name button, .key-name button', function (event) {
        event.preventDefault();
        showInfoModal(page, $(this).data("call"));
    });

    $(document).on('click', '.create-user', function (event) {
        event.preventDefault();
        showConfirmModal('/user/get/create/');
    });

    $(document).on('click', '.add-user', function (event) {
        event.preventDefault();
        showConfirmModal('/user/get/add/');
    });

    $(document).on('click', '.create-group', function (event) {
        event.preventDefault();
        showConfirmModal('/security_group/get/create/');
    });

    $(document).on('click', '.create-key', function (event) {
        event.preventDefault();
        showConfirmModal('/key_pair/get/create/');
    });

    $(document).on('click', '.delete-user, .enable-user, .disable-user, .remove-user, .delete-group, .delete-key', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = ("/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/").slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // --- Initialize Project View ---
    window.loading.current = page;
    window.startProjectUpdateTimer();
    switchPageContent($("#project"), page, window.loading.current, project, [], "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
    $("#project").addClass('active');
});

window.deleteTimer = function () {
    window.setInterval(function () {
    }, 1000)
};

// --- Project Charts ---

charts = {};

function generateQuotaBar(parent, project_used, project_total, label, limit_used, classes) {
    if (parent.find('div.quota-bar').length == 0) {
        limit_used = limit_used === undefined ? limit_used = false : parseInt(limit_used);
        classes = classes === undefined ? ["progress-bar-info", "progress-bar-success", "progress-bar-warning"] : classes;
        project_used = parseInt(project_used);
        project_total = parseInt(project_total);
        var html = $('<div class="progress"></div>');
        if (limit_used != false) {
            var usedWidth = ((project_used / project_total) * 100),
                totalWidth = ((limit_used / project_total) * 100);
            totalWidth = totalWidth - usedWidth;
            if (usedWidth <= totalWidth) {
                html
                    .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'))
                    .append($('<div class="progress-bar ' + classes[1] + '" style="width: ' + totalWidth + "%" + '"></div>'));
            } else {
                html
                    .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'));
            }
            html = $('<div class="quota-bar"><h5>' + label + ' ' + project_used + '/' + limit_used + '/' + project_total + '</h5></div>').append(html);
        } else {
            var usedWidth = ((project_used / project_total) * 100);
            html
                .append($('<div class="progress-bar ' + classes[0] + '" style="width: ' + usedWidth + "%" + '"></div>'));
            html = $('<div class="quota-bar"><h5>' + label + ' ' + project_used + '/' + project_total + '</h5></div>').append(html);
        }
        parent.append(html);
    }
}

function generateQuotaPie(id, data, label) {
    if (data.length == 2) {
        var used = data[0],
            max = data[1];
        data = [
            [used[0], used[1]],
            [max[0], (max[1] - used[1])]
        ];
    } else if (data.length == 3) {
        var used = data[0],
            util = data[1],
            max = data[2];
        if (used[0] >= util[0]) {
            data = [
                [used[0], used[1]],
                [max[0], (max[1] - used[1])]
            ];
        } else {
            data = [
                [used[0], used[1]],
                [util[0], (util[1] - used[1])],
                [max[0], (max[1] - (used[0] + util[0]))]
            ];
        }
    }
    charts[id] = generatePie(id, data, label);

}
function generateInstanceBars(meters, stats) {
    meters = JSON.parse(meters.jsonify());
    stats = JSON.parse(stats.jsonify());
    var counters = [],
        groups = [];
    $(stats).each(function (index, stat) {
        if (stat.chartType == "counter") {
            counters.push(stat);
        }
    });
    var barGroups = {};
    $(counters).each(function (index, element) {
        if (barGroups[element['meterName'].split(".")[0]] === undefined) {
            barGroups[element['meterName'].split(".")[0]] = [];
        }
        barGroups[element['meterName'].split(".")[0]].push(element);
    });
    for (var bar in barGroups) {
        var data = [],
            units,
            id;
        $(barGroups[bar]).each(function (a, statsMeter) {
            $(meters).each(function (b, meterGroup) {
                $(meterGroup.meters).each(function (c, meter) {
                    if (meter.meterType == statsMeter.meterName) {
                        data.push([meter.label, statsMeter.utilization]);
                        units = statsMeter.unitMeasurement;
                        id = meterGroup.id;
                    }
                });
            });
        });
        units = units === undefined ? "" :
            units == "B/s" ? "bytes/second" : units;
        id = id === undefined ? console.log("Bar group id never defined.") : id;
        groups.push([bar, units, data, id]);
    }
    $(groups).each(function (c, d) {
        if (document.getElementById(d[0]) === null) {
            var groupId = "#" + d[3];
            $(groupId).append($($('<div id="' + d[0] + '" class="col-sm-6 no-padding" style="margin-left:-15px;"></div>')));
            charts[d[0]] = generateBar(d[0], d[1], d[2]);
        }
    });
}

window.updateProjectContent = function () {
    var page = $("#page-content"),
        project = $("#project-container"),
        instances = $("#instances-container"),
        storage = $("#storage-container"),
        networking = $("#networking-container"),
        usersSecurity = $("#users-security-container");
    switch (window.loading.current.selector) {
        case project.selector:
            stealthRefreshContainer(page, project, "/projects/" + CURRENT_PROJECT_ID + "/get_project_panel/");
            break;
        case instances.selector:
            stealthRefreshContainer(page, instances, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
            break;
        case storage.selector:
            stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
            break;
        case networking.selector:
            stealthRefreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
            break;
        case usersSecurity.selector:
            stealthRefreshContainer(page, usersSecurity, "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
            break;
    }
};

window.startProjectUpdateTimer = function () {
    if (window.projectUpdateTimer) {
        window.clearInterval(window.projectUpdateTimer);
    }
    window.projectUpdateTimer = setInterval(function () {
        window.updateProjectContent();
    }, 60000)
};

// --- Build Instance ---

$(function () {
    $("#instance-wizard").click(function (event) {
        event.preventDefault();
        showConfirmModal('/projects/get/instance_wizard/' + CURRENT_PROJECT_ID + '/');
    });
});

// Declare and Initialize variables on document ready
var currentSection = "initialize",
    bamParams;

$(function () {
    currentSection = "initialize";
    bamParams = {
        "instance": {
            "section": "#bam-instance-section",
            "inputs": {
                "name": {
                    "element": $("#instance-name"),
                    "validation": function () {
                        return $(this.element).valid();
                    },
                    "value": ""
                },
                "image": {
                    "element": $("#instance-image"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "flavor": {
                    "element": $("#instance-flavor"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "network": {
                    "element": $("#instance-network"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "ip": {
                    "element": $("#instance-ip"),
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
                    "element": $("#image-name"),
                    "validation": function () {
                        return $(this.element).valid();
                    },
                    "value": ""
                },
                "container": {
                    "element": $("#image-container"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "disk": {
                    "element": $("#image-disk"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "type": {
                    "element": $("#image-type"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "importLocal": {
                    "element": $("#image-local"),
                    "validation": function () {
                        if ($("#image-type").val() == "image_file") {
                            return $(this.element).valid();
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "importRemote": {
                    "element": $("#image-remote"),
                    "validation": function () {
                        if ($("#image-type").val() == "image_url") {
                            return $(this.element).valid();
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "os": {
                    "element": $("#image-os"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "visibility": {
                    "element": $("#image-visibility"),
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
                    "element": $("#volume-existing"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "name": {
                    "element": $("#volume-name"),
                    "validation": function () {
                        if ($("#volume-name").val() == "create") {
                            return $(this.element).valid();
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "size": {
                    "element": $("#volume-size"),
                    "validation": function () {
                        if ($("#volume-existing").val() == "create") {
                            return $(this.element).valid();
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "type": {
                    "element": $("#volume-type"),
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
                "key": {
                    "element": $("#instance-key"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "newKey": {
                    "element": $("#key-name"),
                    "validation": function () {
                        if ($("#instance-key").val() == "create") {
                            return $(this.element).valid();
                        } else {
                            return true;
                        }
                    },
                    "value": ""
                },
                "group": {
                    "element": $("#instance-group"),
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
                    "element": $("#group-name"),
                    "validation": function () {
                        return $(this.element).valid();
                    },
                    "value": ""
                },
                "description": {
                    "element": $("#group-description"),
                    "validation": function () {
                        if (this.element.val() == "") {
                            this.element.val("none");
                        }
                        return $(this.element).valid();
                    },
                    "value": ""
                },
                "transport": {
                    "element": $("#group-transport"),
                    "validation": function () {
                        return true;
                    },
                    "value": ""
                },
                "ports": {
                    "element": $("#group-ports"),
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
    switchSections(currentSection, "instance");
}

function changeBamSection(button) {
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
}

function updateProgressSection() {
    $("#bam-progress-section").find("ul").children().each(function () {
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
                $(".bam-image-upload-bar > .progress-bar").css("width", 0);
                xhr.upload.onprogress = function (e) {
                    if (e.lengthComputable) {
                        var percentage = Math.floor(100 * parseInt(e.loaded) / parseInt(e.total));
                        $(".bam-image-upload-bar > .progress-bar").css("width", percentage);
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
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, instances, "/projects/" + CURRENT_PROJECT_ID + "/get_instance_panel/");
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
                    showMessage('error', data.message);
                    error = true;
                    return false;
                }
                if (data.status == 'success') {
                    stealthRefreshContainer(page, usersSecurity, "/projects/" + CURRENT_PROJECT_ID + "/get_users_security_panel/");
                    step++;
                    updateProgress(step, steps, "Group Created");
                    secGroup = bamParams["group"].inputs["name"].value;
                }
            }).fail(function () {
                showMessage("error", "Error: Could not create security group");
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
            PROJECT_ID +
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
                    $(".bam-confirm-name").html(bamParams.instance.inputs.name.value.toString());
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
                            showMessage('error', data.message);
                            error = true;
                            return false;
                        }

                        if (data.status == 'success') {
                            stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
                            step++;
                            updateProgress(step, steps, "Volume Created");
                            volume = data.volume_id.toString();
                        }
                    })
                    .fail(function () {
                        showMessage("error", "Error: Could not create volume");
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
                                showMessage('error', data.message);
                                error = true;
                                return false;
                            }

                            if (data.status == 'success') {

                                stealthRefreshContainer(page, storage, "/projects/" + CURRENT_PROJECT_ID + "/get_storage_panel/");
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
                    if (bamParams.security.inputs.ip.value != "none") {
                        updateProgress(step, steps, "Assigning IP");
                        assignIp = $.getJSON(
                            '/assign_floating_ip/' +
                            assignableFips.getItem(bamParams["security"].inputs["ip"].value).option + '/' +
                            instanceId + '/' +
                            PROJECT_ID + '/')
                            .done(function (data) {
                                if (data.status == 'error') {
                                    showMessage('error', data.message);
                                    error = true;
                                    return false;
                                }
                                if (data.status == 'success') {
                                    stealthRefreshContainer(page, networking, "/projects/" + CURRENT_PROJECT_ID + "/get_networking_panel/");
                                    step++;
                                    updateProgress(step, steps, "IP Assigned");
                                    $(".bam-confirm-ip").html(fips.getItem(bamParams["security"].inputs["ip"].value).ip);
                                }
                            })
                            .fail(function () {
                                showMessage("error", "Error: Could not assign ip");
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
                    });
                });
            });
        });
    });
}

function updateProgress(stepCount, steps, stepLabel) {
    $(".bam-overall-progress-bar").css("width", (stepCount / steps) * 100 + "%");
    $(".bam-overall-progress-label").html(stepLabel);
}