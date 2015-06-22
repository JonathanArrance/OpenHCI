// Declare click events after document has loaded
$(function () {

    // --- Create ---

    $("#create-instance").click(function (event) {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        // Create Form
        var form =
            $("<div></div>").prop("id", "instance-dialog-form").prop("title", "Create Instance")
                .append($("<h6>Create a new instance. All form fields are required.</h6>").addClass("validateTips"))
                .append($("<form></form>")
                    .append($("<fieldset></fieldset>")
                        .append($("<label>Instance Name</label>").prop("for", "name"))
                        .append($("<input></input>").prop("id", "name").prop("name", "name").prop("type", "text")))
                    .append($("<fieldset></fieldset>").addClass("tall")
                        .append($("<legend>Instance Options</legend>"))
                        .append($("<label>Image</label>").prop("for", "image"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "image").prop("name", "image")))
                        .append($("<label>Flavor</label>").prop("for", "flavor"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "flavor").prop("name", "flavor")))
                        .append($("<label>Boot Options</label>").prop("for", "Boot Options"))
                        .append($("<span>(help)<span>").addClass("helper").prop("title", 'To store all instance data on a physical volume, choose "Boot From Volume"; otherwise, all instance data will be lost on instance deletion.'))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "boot-option").prop("name", "boot-option")
                                .append($("<option>Boot Ephemeral</option>").prop("value", "false"))
                                .append($("<option>Boot From Volume</option>").prop("value", "true"))
                                .click(function (event) {
                                    event.preventDefault();
                                    toggleBootOptions($("#boot-option").val());
                                }))))
                    .append($("<fieldset></fieldset>").addClass("tall")
                        .append($("<legend>Network & Security</legend>"))
                        .append($("<label>Private Network</label>").prop("for", "network"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "network").prop("name", "network")))
                        .append($("<label>Security Group</label>").prop("for", "group"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "group").prop("name", "group")))
                        .append($("<label>Security Key</label>").prop("for", "key"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "key").prop("name", "key"))))
                    .append($("<fieldset></fieldset>").prop("id", "instance-boot-options").css("display", "None").addClass("wide")
                        .append($("<legend>Boot Volume Options</legend>"))
                        .append($("<label>Boot Volume Name</label>").prop("for", "boot-name").css("margin-top", "15px"))
                        .append($("<input></input>").prop("id", "boot-name").prop("name", "boot-name").prop("type", "text").prop("placeholder", "Optional"))
                        .append($("<label>Boot Volume Type</label>").prop("for", "boot-type").css("margin-top", "14px").css("vertical-align", "top"))
                        .append($("<div></div").addClass("styled-select")
                            .append($("<select></select>").prop("id", "boot-type").prop("name", "boot-type")))
                        .append($("<label>Boot Volume Size</label>").prop("for", "boot-size"))
                        .append($("<input></input>").prop("id", "boot-size").prop("name", "boot-size").prop("type", "text"))));
        // Populate selects
        refreshSelect(form.find("#group"), secGroupInstOpts);
        refreshSelect(form.find("#key"), secKeyInstOpts);
        refreshSelect(form.find("#network"), privNetInstOpts);
        refreshSelect(form.find("#image"), images);
        refreshSelect(form.find("#flavor"), flavors);
        refreshSelect(form.find("#boot-type"), volumeTypes);
        // Open dialog form
        form.dialog({
            autoOpen: true,
            height: 390,
            width: 475,
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
                "Create Instance": function () {
                    // Create Instance
                    createInstance($("#name"), $("#group"), $("#key"), $("#network"), $("#image"), $("#flavor"), $("#boot-option"), $("#boot-name"), $("#boot-type"), $("#boot-size"));
                }
            },
            close: function () {
                // Reset form validation
                resetUiValidation([$("#name"), $("#group"), $("#key"), $("#network"), $("#image"), $("#flavor"), $("#boot-option"), $("#boot-name"), $("#boot-type"), $("#boot-size")]);
                // Remove dialog form
                $(this).remove();
            }
        }).css("overflow", "hidden");
    });

    // --- Delete ---

    $(document).on('click', '.delete-instance', function (event) {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        // Get target row element, get id from that element and use that to get the name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text")),
            boot = instances.items[id].bootVol != undefined;
        if (boot) {
            // Create form
            $("<div></div>").prop("id", "instance-delete-confirm-form").prop("title", "Delete Instance")
                .append($("<p></p>").css("text-align", "center").html("The instance " + instance.text() + " has a boot volume, do you want to delete it along with the instance? All instance data will be lost."))
                .append($("<label></label>").prop("for", "delete-boot").html("Delete boot volume:"))
                .append($("<input></input>").prop("id", "delete-boot").prop("type", "checkbox"))
                .dialog({
                    autoOpen: true,
                    height: 200,
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

                            // Delete instance
                            var deleteBootVol = $("#delete-boot").prop('checked');
                            deleteInstance(id, instance, targetRow, deleteBootVol);

                            // Close Dialog form
                            $(this).remove();
                        }
                    }
                });
        } else {
            // Create form
            $("<div></div>").prop("id", "instance-delete-confirm-form").prop("title", "Delete Instance")
                .append($("<p></p>").css("text-align", "center").html("Delete " + instance.text() + "?"))
                .dialog({
                    autoOpen: true,
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

                            // Delete instance
                            deleteInstance(id, instance, targetRow, false);

                            // Close Dialog form
                            $(this).remove();
                        }
                    }
                });
        }
    });

    // --- Pause ---

    $(document).on('click', '.pause-instance', function (event) {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));
        // Create form
        $("<div></div>").prop("id", "instance-pause-confirm-form").prop("title", "Pause Instance")
            .append($("<p></p>").css("text-align", "center").html("Pause " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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
                        // Pause instance
                        pauseInstance(id, instance, targetRow);
                        // Close Dialog form
                        $(this).remove();
                    }
                }
            });
    });

    // --- Unpause ---

    $(document).on('click', '.unpause-instance', function (event) {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));
        // Add instance-name-text to delete-confirm-form
        $('div#instance-unpause-confirm-form > p > span.instance-name').empty().append(instance.text());
        // Create form
        $("<div></div>")
            .prop("id", "instance-unpause-confirm-form")
            .prop("title", "Unpause Instance")
            .css("display", "none")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Unpause " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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
                        // Unpause Instance
                        unpauseInstance(id, instance, targetRow);
                        // Close dialog form
                        $(this).remove();
                    }
                }
            });
    });

    // --- Suspend ---

    $(document).on('click', '.suspend-instance', function (event) {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        // Get target row element, get id from that element and use that to get the instance-name-text
        var targetRow = $(this).parent().parent(),
            id = $(targetRow).attr("id"),
            instance = $(document.getElementById(id + "-name-text"));
        // Create form
        $("<div></div>")
            .prop("id", "instance-suspend-confirm-form")
            .prop("title", "Suspend Instance")
            .append($("<p></p>")
                .css("text-align", "center")
                .html("Suspend " + instance.text() + "?"))
            .dialog({
                autoOpen: true,
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
                        // Suspend instance
                        suspendInstance(id, instance, targetRow);
                        // Close dialog form
                        $(this).remove();
                    }
                }
            });
    });
});

// --- Resume ---

$(document).on('click', '.resume-instance', function (event) {
    // Prevent scrolling to top of page on click
    event.preventDefault();
    // Get target row element, get id from that element and use that to get the instance-name-text
    var targetRow = $(this).parent().parent(),
        id = $(targetRow).attr("id"),
        instance = $(document.getElementById(id + "-name-text"));
    // Create form
    $("<div></div>")
        .prop("id", "instance-resume-confirm-form")
        .prop("title", "Resume Instance")
        .append($("<p></p>")
            .css("text-align", "center")
            .html("Resume " + instance.text() + "?"))
        .dialog({
            autoOpen: true,
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
                    // Resume instance
                    resumeInstance(id, instance, targetRow);
                    // Close dialog form
                    $(this).remove();
                }
            }
        });
});

function toggleBootOptions(option) {
    if (option == "true") {
        $("#instance-dialog-form").dialog({height: 550});
        $("#instance-boot-options").show(0);
    } else {
        $("#instance-dialog-form").dialog({height: 390});
        $("#instance-boot-options").hide(0);
    }
}

function createInstance(name, secGroup, secKey, network, image, flavor, bootOption, bootName, bootType, bootSize) {
    // Gather inputs
    var allFields = $([]).add(name).add(secGroup).add(secKey).add(network).add(image).add(flavor).add(bootOption).add(bootName).add(bootType).add(bootSize);
    // Remove UI validation flags
    clearUiValidation(allFields);
    // Validate form inputs
    var isValid =
        checkLength(name, "Instance Name", standardStringMin, standardStringMax) &&
        checkCharfield(name, "Instance name") &&
        checkDuplicateName(name, instanceOpts);
    if (isValid) {
        if (bootOption.val() == "true") {
            if (bootName.val() != "") {
                isValid =
                    checkCharfield(bootName, "Volume name") &&
                    checkDuplicateName(bootName, volumes) &&
                    checkSize(bootSize, "Volume Size must be greater than 0.", 1, 0) &&
                    checkBootSize(bootSize, flavor.val()) &&
                    checkStorage(bootSize);
            } else {
                isValid =
                    checkDuplicateName(bootName, volumes) &&
                    checkSize(bootSize, "Volume Size must be greater than 0.", 1, 0) &&
                    checkBootSize(bootSize, flavor.val()) &&
                    checkStorage(bootSize);
            }
        }
    }
    // If Valid, create instance
    if (isValid) {
        // Remove dialog form
        $("#instance-dialog-form").remove();
        // Confirmed Selections
        var confName = name.val(),
            confSecGroup = secGroup.val(),
            confSecKey = secKey.val(),
            confNetwork = network.val(),
            confImage = images.items[image.val()].id,
            confFlavor = flavors.items[flavor.val()].id,
            confBoot = bootOption.val(),
            confBootName,
            confBootType,
            confBootSize;
        // Check boot options
        if (confBoot == "true") {
            confBootName = bootName.val() == "" ? "none" : bootName.val();
            confBootType = bootType.val() == "" ? "none" : bootType.val();
            confBootSize = bootSize.val();
        } else {
            confBootName = "none";
            confBootType = "none";
            confBootSize = "none";
        }
        // Show toast message
        message.showMessage('notice', 'Creating New Instance ' + confName);
        // Hide widget buttons and disable widget view links
        setVisible('#create-instance', false);
        disableLinks(true);
        // Initialize progressbar and make it visible if hidden
        $("#instance_progressbar").progressbar({value: false});
        disableProgressbar($("#instance_progressbar"), "instances", false);
        // Make AJAX call and handle response
        $.getJSON('/create_instance/' + confName + '/' + confSecGroup + '/nova/' + confFlavor + '/' + confSecKey + '/' + confImage + '/' + confNetwork + '/' + PROJECT_ID + '/' + confBoot + '/' + confBootSize + '/' + confBootName + '/' + confBootType + '/')
            .done(function (data) {
                if (data.status == 'error') {
                    // Show toast message
                    message.showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    // Show toast message
                    message.showMessage('success', data.message);
                    // Add new row
                    addInstance(data);
                }
            })
            .fail(function () {
                // Show toast message
                message.showMessage('error', 'Server Fault');
            })
            .always(function () {
                // Reset interface
                checkAssignFip();
                disableProgressbar($("#instance_progressbar"), "instances", true);
                setVisible('#create-instance', true);
                disableLinks(false);
                resetUiValidation(allFields);
            });
    }
}

function addInstance(data) {
    // Create new row element and append it to instance_list
    $("<tr></tr>").prop("id", data.server_info.server_id)
        .append($("<td></td>").prop("id", data.server_info.server_id + '-name-cell')
            .append($("<a></a>").prop("href", '/' + PROJECT_ID + '/' + data.server_info.server_id + '/instance_view/').addClass("disable-link")
                .append($("<span></span>").prop("id", data.server_info.server_id + '-name-text').html(data.server_info.server_name.toString()))))
        .append($("<td></td>").prop("id", data.server_info.server_id + '-status-cell').html("ACTIVE"))
        .append($("<td></td>").prop("id", data.server_info.server_id + '-os-cell').html(data.server_info.server_os.toString() + ' / ' + data.server_info.server_flavor.toString()))
        .append($("<td></td>").prop("id", data.server_info.server_id + '-actions-cell')
            .append($("<a></a>").prop("href", "#").prop("class", "open-instance-console").on("click", function () {
                window.open(
                    data.server_info.novnc_console,
                    "_blank",
                    "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
            }).html("console"))
            .append($("<span></span>").prop("class", "instance-actions-pipe").html(" | "))
            .append($("<a></a>").prop("href", "#").prop("class", 'pause-instance ' + data.server_info.server_id + '-disable-action').html("pause"))
            .append($("<span></span>").prop("class", "instance-actions-pipe").html(" | "))
            .append($("<a></a>").prop("href", "#").prop("class", 'suspend-instance ' + data.server_info.server_id + '-disable-action').html("suspend"))
            .append($("<span></span>").prop("class", "instance-actions-pipe").html(" | "))
            .append($("<a></a>").prop("href", "#").prop("class", 'delete-instance ' + data.server_info.server_id + '-disable-action').html("delete")))
        .appendTo($("#instance_list")).fadeIn();
    // Check table length, remove placeholder if necessary
    if ($('#instance_list tr').length >= 2) {
        $('#instance_placeholder').fadeOut().remove();
    }
    // Add to instances and consoleLinks
    instances.setItem(data.server_info.server_id, {
            id: data.server_info.server_id,
            name: data.server_info.server_name,
            status: data.server_info.server_status,
            flavor: data.server_info.server_flavor,
            os: data.server_info.server_os,
            console: data.server_info.novnc_console
        }
    );
    consoleLinks.setItem(data.server_info.server_id, {
            link: data.server_info.novnc_console,
            html: '<a href=\"' + data.server_info.novnc_console + '\" class=\"open-instance-console\" onClick=\"window.open(this.href,\'_blank\',\'toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435\'); return false;\">console</a>'
        }
    );
    // Add to selects
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance"), attachableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#assign_instance"), assignableInstances);
    addToSelect(data.server_info.server_id, data.server_info.server_name, $("#instance_to_snap"), instanceOpts);
    if (!data.volume.none) {
        $("<tr></tr>").prop("id", data.volume.volume_id.toString()).addClass("volume-mounted")
            .append($("<td></td>").prop("id", data.volume.volume_id + '-name-cell')
                .append($("<a></a>").prop("href", '/projects/' + PROJECT_ID + '/volumes/' + data.volume.volume_id + '/view/').addClass("disable-link")
                    .append($("<span></span>").prop("id", data.volume.volume_id + '-name-text').html(data.volume.volume_name.toString()))))
            .append($("<td></td>").prop("id", data.volume.volume_id + '-attached-cell')
                .append($("<span></span>").html(data.server_info.server_name)))
            .append($("<td></td>").prop("id", data.volume.volume_id + '-actions-cell'))
            .appendTo($("#volume_list")).fadeIn();
        if ($("#volume_list tr").length >= 2) {
            $("#volume_placeholder").fadeOut().remove();
            setVisible('#create-snapshot', true);
        }
        instances.items[data.server_info.server_id]['bootVol'] = data.volume.volume_id;
        volumes.setItem(data.volume.volume_id, {
            size: data.volume.volume_size,
            name: data.volume.volume_name,
            type: data.volume.volume_type,
            value: data.volume.volume_id,
            option: data.volume.volume_name,
            attached: "true",
            bootable: "true"
        });
        snapshotVolumes.setItem(data.volume.volume_id, {
            value: data.volume.volume_id,
            option: data.volume.volume_name
        });
        // Update select
        refreshSelect($("#snap_volume"), snapshotVolumes);
        refreshSelect("#bam-volume-select-existing", snapshotVolumes);
        $('<option></option>').val("none").html("Skip Adding Storage").prop("selected", "selected").prependTo($("#bam-volume-select-existing"));
        $('<option></option>').val("create").html("Create Volume").appendTo($("#bam-volume-select-existing"));
        // Update usedStorage
        updateUsedStorage();
        updateStorageBar();
    }
}

function deleteInstance(id, name, row, deleteBootVol) {
    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;
    // Show toast message
    message.showMessage('notice', "Deleting " + confInstance + ".");
    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = actionsCell.html();
    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("delete-instance", true);
    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);
    // Clear clicked action link and replace with loader
    actionsCell.empty()
        .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/' + deleteBootVol + '/delete_instance/')
        .done(function (data) {
            if (data.status == 'error') {
                // Show toast message
                message.showMessage('error', data.message);
                // Restore actions cell html
                actionsCell.empty()
                    .append(actionsHtml);
            }
            if (data.status == 'success') {
                // Show toast message
                message.showMessage('success', data.message);
                // Remove row
                confRow.fadeOut().remove();
                // Update selects
                removeFromSelect(confId, $("#instance"), attachableInstances);
                removeFromSelect(confId, $("#assign_instance"), assignableInstances);
                // If last assignable instance, or no available ips, hide "Assign" IP button
                if (assignableFips.length <= 0 || assignableInstances.length <= 0) {
                    setVisible('#assign_ip', false);
                }
                // Unattach volumes
                for (var i = 0; i < data.vols.length; i++) {
                    if (volumes.items[data.vols[i][0]] != undefined) {
                        $(document.getElementById(data.vols[i][0] + '-attached-cell')).empty()
                            .append($("<span></span>").prop("id", data.vols[i][0] + '-attached-placeholder').html("No Attached Instance").fadeIn())
                            .parent().removeClass("volume-attached");
                        $(document.getElementById(data.vols[i][0] + '-actions-cell')).empty()
                            .append($("<a></a>").prop("href", "#").prop("class", "attach-volume").html("attach").fadeIn())
                            .append($("<span></span>").prop("class", "volume-actions-pipe").html(" | ").fadeIn())
                            .append($("<a></a>").prop("href", "#").prop("class", "clone-volume").html("clone").fadeIn())
                            .append($("<span></span>").prop("class", "volume-actions-pipe").html(" | ").fadeIn())
                            .append($("<a></a>").prop("href", "#").prop("class", "revert-volume").html("revert").fadeIn())
                            .append($("<span></span>").prop("class", "volume-actions-pipe").html(" | ").fadeIn())
                            .append($("<a></a>").prop("href", "#").prop("class", "delete-volume").html("delete").fadeIn());
                        snapshotVolumes.setItem(data.vols[i][0], {
                            value: data.vols[i][0],
                            option: volumes.items[data.vols[i][0]].name
                        })
                    }
                }
                // Unassign floating IPs
                for (var j = 0; j < data.floating_ip.length; j++) {
                    $(document.getElementById(data.floating_ip_id[j][0] + '-instance-cell')).empty()
                        .append($("<span></span>").prop("id", data.floating_ip[j][0] + '-instance-name').html("None").fadeIn())
                        .parent().removeClass("fip-assigned");
                    $(document.getElementById(data.floating_ip_id[j][0] + '-actions-cell')).empty()
                        .append($("<a></a>").prop("id", data.floating_ip_id[j][0]).prop("class", "deallocate-ip").prop("href", "#").html("deallocate").fadeIn());
                    assignableFips.setItem(data.floating_ip_id[j][0], {
                        value: data.floating_ip_id[j][0],
                        option: fips.getItem(data.floating_ip_id[j][0]).ip
                    })
                }
                if (deleteBootVol) {
                    var bootId = instances.items[confId].bootVol;
                    // Remove row
                    $(document.getElementById(bootId)).fadeOut().remove();
                    // Remove volume
                    volumes.removeItem(bootId);
                    snapshotVolumes.removeItem(bootId);
                    // Update select
                    refreshSelect($("#snap_volume"), snapshotVolumes);
                    refreshSelect("#bam-volume-select-existing", snapshotVolumes);
                    $('<option></option>').val("none").html("Skip Adding Storage").prop("selected", "selected").prependTo($("#bam-volume-select-existing"));
                    $('<option></option>').val("create").html("Create Volume").appendTo($("#bam-volume-select-existing"));
                    // Update usedStorage
                    updateUsedStorage();
                    updateStorageBar();
                    // If last row, append placeholder
                    if ($('#volume_list tr').length < 2) {
                        $(table).append(placeholder).fadeIn();
                        setVisible('#create-snapshot', false);
                    }
                }
                // Remove from instances
                instances.removeItem(confId);
                instanceOpts.removeItem(confId);
                // Update Selects
                refreshSelect('#instance_to_snap', instanceOpts);
                refreshSelect($("#bam-security-ip"), assignableFips);
                $('<option></option>').val("none").html("Skip Attaching IP").prop("selected", "selected").prependTo($("#bam-security-ip"));
                refreshSelect("#bam-volume-select-existing", snapshotVolumes);
                $('<option></option>').val("none").html("Skip Adding Storage").prop("selected", "selected").prependTo($("#bam-volume-select-existing"));
                $('<option></option>').val("create").html("Create Volume").appendTo($("#bam-volume-select-existing"));
                // If last row, append placeholder
                if ($('#instance_list tr').length < 2) {
                    $("<tr></tr>").prop("id", "instance_placeholder")
                        .append($("<td></td>")
                            .append($("<p></p>")
                                .append($("<i></i>").html("This project has no instances"))))
                        .append($("<td></td>"))
                        .append($("<td></td>")).appendTo($("#instance_list")).fadeIn();
                }
            }
        })
        .fail(function () {
            message.showMessage('error', 'Server Fault');
            // Restore actions cell html
            actionsCell.empty()
                .append(actionsHtml);
        })
        .always(function () {
            // Hide progressbar and enable widget view links
            checkAssignFip();
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("delete-instance", false);
            disableLinks(false);
        });
}

function pauseInstance(id, name, row) {
    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;
    // Show toast message
    message.showMessage('notice', "Pausing " + confInstance + ".");
    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = actionsCell.html();
    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("pause-instance", true);
    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);
    // Clear clicked action link and replace with loader
    actionsCell.empty()
        .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/pause_server/')
        .done(function (data) {
            if (data.status == 'error') {
                // Show toast message
                message.showMessage('error', data.message);
                // Restore actions cell html
                actionsCell.empty()
                    .append(actionsHtml);
            }
            if (data.status == 'success') {
                // Show toast message
                message.showMessage('success', data.message);
                var statusCell = $(document.getElementById(confId + "-status-cell"));
                // Update status cell
                statusCell.empty()
                    .append("PAUSED").fadeIn();
                // Update actions-cell
                actionsCell.empty()
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "unpause-instance").prop("href", "#").html("unpause").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "delete-instance").prop("href", "#").html("delete").fadeIn());
                // Add paused class
                confRow.addClass("instance-paused");
                // Update instance
                instances.items[confId].status = "PAUSED";
            }
        })
        .fail(function () {
            // Show toast message
            message.showMessage('error', 'Server Fault');
            // Restore actions cell html
            actionsCell.empty()
                .append(actionsHtml);
        })
        .always(function () {
            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("pause-instance", false);
            disableLinks(false);
        });
}

function unpauseInstance(id, name, row) {
    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;
    // Show toast message
    message.showMessage('notice', "Unpausing " + confInstance + ".");
    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = actionsCell.html();
    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("unpause-instance", true);
    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);
    // Clear clicked action link and replace with loader
    actionsCell.empty()
        .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/unpause_server/')
        .done(function (data) {
            if (data.status == 'error') {
                // Show toast message
                message.showMessage('error', data.message);
                // Restore actions cell html
                actionsCell.empty()
                    .append(actionsHtml);
            }
            if (data.status == 'success') {
                // Show toast message
                message.showMessage('success', data.message);
                var statusCell = $(document.getElementById(confId + "-status-cell"));
                // Update status cell
                statusCell.empty()
                    .append("ACTIVE").fadeIn();

                // Update actions-cell
                actionsCell.empty()
                    .append($("<a></a>").prop("href", "#").prop("class", "open-instance-console").on("click", function () {
                        window.open(consoleLinks.items[id].link, "_blank", "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                    }).html("console"))
                    .append($("<span></span>").prop("class", "instance-actions-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "pause-instance").prop("href", "#").html("pause").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "suspend-instance").prop("href", "#").html("suspend").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "delete-instance").prop("href", "#").html("delete").fadeIn());
                // Remove paused class
                confRow.removeClass("instance-paused");
                // Update instance
                instances.items[confId].status = "ACTIVE";
            }
        })
        .fail(function () {
            // Show toast message
            message.showMessage('error', 'Server Fault');
            // Restore Actions html
            actionsCell.empty()
                .append(actionsHtml).fadeIn();
        })
        .always(function () {
            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("unpause-instance", false);
            disableLinks(false);
        });
}

function suspendInstance(id, name, row) {
    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;
    // Show toast message
    message.showMessage('notice', "Suspending " + confInstance + ".");
    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = actionsCell.html();
    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("suspend-instance", true);
    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);
    // Clear clicked action link and replace with loader
    actionsCell.empty()
        .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/suspend_server/')
        .done(function (data) {
            if (data.status == 'error') {
                // Show toast message
                message.showMessage('error', data.message);
                // Restore actions cell html
                actionsCell.empty()
                    .append(actionsHtml);
            }
            if (data.status == 'success') {
                // Show toast message
                message.showMessage('success', data.message);
                var statusCell = $(document.getElementById(confId + "-status-cell"));

                // Update status cell
                statusCell.empty()
                    .append("SUSPENDED").fadeIn();
                // Update actions-cell
                actionsCell.empty()
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "resume-instance").prop("href", "#").html("resume").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "delete-instance").prop("href", "#").html("delete").fadeIn());
                // Add paused class
                confRow.addClass("instance-suspended");
                // Update instance
                instances.items[confId].status = "SUSPENDED";
            }
        })
        .fail(function () {
            // Show toast message
            message.showMessage('error', 'Server Fault');
            // Restore Actions html
            actionsCell.empty()
                .append(actionsHtml).fadeIn();
        })
        .always(function () {
            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("suspend-instance", false);
            disableLinks(false);
        });
}

function resumeInstance(id, name, row) {
    // Confirmed Selections
    var confId = id,
        confInstance = name.text(),
        confRow = row;
    // Show toast message
    message.showMessage('notice', "Resuming " + confInstance + ".");
    // Store actions cell html
    var actionsCell = $(document.getElementById(confId + "-actions-cell"));
    var actionsHtml = actionsCell.html();
    // Disable widget view links and instance actions
    disableLinks(true);
    disableActions("resume-instance", true);
    // Initialize progressbar and make it visible
    $("#instance_progressbar").progressbar({value: false});
    disableProgressbar($("#instance_progressbar"), "instances", false);
    // Clear clicked action link and replace with loader
    actionsCell.empty()
        .append($("<div></div>").prop("id", confId + '-loader').prop("class", "ajax-loader").fadeIn());
    $.getJSON('/server/' + PROJECT_ID + '/' + confId + '/resume_server/')
        .done(function (data) {
            if (data.status == 'error') {
                // Show toast message
                message.showMessage('error', data.message);
                // Restore actions cell html
                actionsCell.empty().append(actionsHtml);
            }
            if (data.status == 'success') {
                // Show toast message
                message.showMessage('success', data.message);
                var statusCell = $(document.getElementById(confId + "-status-cell"));
                // Update status cell
                statusCell.empty()
                    .append("ACTIVE").fadeIn();
                // Update actions-cell
                actionsCell.empty()
                    .append($("<a></a>").prop("href", "#").prop("class", "open-instance-console").on("click", function () {
                        window.open(consoleLinks.items[id].link, "_blank", "toolbar=no, location=no, status=no, menubar=no, titlebar = no, scrollbars=yes, resizable=yes, width=720, height=435")
                    }).html("console"))
                    .append($("<span></span>").prop("class", "instance-actions-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "pause-instance").prop("href", "#").html("pause").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "suspend-instance").prop("href", "#").html("suspend").fadeIn())
                    .append($("<span></span>").prop("class", "instance-action-pipe").html(" | ").fadeIn())
                    .append($("<a></a>").prop("id", confId + '-disable-action').prop("class", "delete-instance").prop("href", "#").html("delete").fadeIn());
                // Remove paused class
                confRow.removeClass("instance-suspended");
                // Update instance
                instances.items[confId].status = "ACTIVE";
            }
        })
        .fail(function () {
            // Show toast message
            message.showMessage('error', 'Server Fault');
            // Restore Actions html
            actionsCell.empty()
                .append(actionsHtml).fadeIn();
        })
        .always(function () {
            // Hide progressbar, enabled instance actions and widget view links
            disableProgressbar($("#instance_progressbar"), "instances", true);
            disableActions("resume-instance", false);
            disableLinks(false);
        });
}
