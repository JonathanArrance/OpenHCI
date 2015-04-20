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

    // --- Build-A-Machine ---

    $(function () {

        // Open modal form when delete-project button clicked
        $("#create-machine").click(function (event) {

            // Prevent scrolling to top of page on click
            event.preventDefault();

            $("#build-a-machine-form").dialog("open");
        });

        $("#build-a-machine-form").dialog({
            autoOpen: false,
            height: 325,
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
            close: function () {
            }
        });

        $("#bam-next-button").click(function (event) {

            // Prevent scrolling to top of page
            event.preventDefault();

            // Handle UI Validation for each section of the wizard by checking inputs when the user hits next.
            // If the input's aren't valid the user can't proceed to the next section
            // If the inputs are valid, add them to the bamInputs dictionary to be used to make the API calls
            switch (currentSection) {

                case "instance":

                    var instanceName = $("#bam-instance-name");
                    clearUiValidation(instanceName);

                    var isInstanceValid =
                        checkLength(instanceName, "Instance Name", 3, 16) &&
                        checkDuplicateName(instanceName, instanceOpts);

                    if (isInstanceValid) {

                        bamInputs["instance-name"] = instanceName.val();
                        bamInputs["instance-image-input"] = "select"; // TODO: IMPLEMENT UPLOAD IMAGE

                        if (bamInputs["instance-image-input"] == "select") {
                            bamInputs["instance-image"] = $("#bam-select-image-name").val();
                        } else if (bamInputs["instance-image-input"] == "upload") {
                            // TODO: IMPLEMENT UPLOAD IMAGE
                        }

                        bamInputs["instance-flavor"] = $("#bam-flavor-name").val();
                        changeBamSection("key");

                        console.log(bamInputs["instance-name"]);
                        console.log(bamInputs["instance-image"]);
                        console.log(bamInputs["instance-flavor"]);
                    }

                    break;

                case "key":

                    var keyInput = $('input[name=bam-select-key-input]:checked').val();

                    if (keyInput == "select") {

                        bamInputs["key"] = $("#bam-select-key-name").val();
                        changeBamSection("volume");
                        console.log(bamInputs["key"]);
                    }

                    if (keyInput == "create") {

                        var key = $("#bam-create-key-name");
                        clearUiValidation(key);

                        var isKeyValid = checkLength(key, "Key name", 3, 16);

                        if (isKeyValid) {

                            bamInputs["key"] = key.val();
                            changeBamSection("volume");
                            console.log(bamInputs["key"]);
                        }
                    }

                    break;

                case "volume":

                    var volumeName = $("#bam-volume-name"),
                        volumeSize = $("#bam-volume-size"),
                        volumeType = $("#bam-volume-type"),
                        volumeFields = $([]).add(volumeName).add(volumeSize).add(volumeType);
                    clearUiValidation(volumeFields);

                    var isVolumeValid =
                        checkLength(volumeName, "Volume Name", 3, 16) &&
                        checkDuplicateName(volumeName, volumes) &&
                        checkSize(volumeSize, "Volume Size must be greater than 0.", 1, 0) &&
                        checkStorage(volumeSize);

                    if (isVolumeValid) {

                        bamInputs["volume-name"] = volumeName.val();
                        bamInputs["volume-size"] = volumeSize.val();
                        bamInputs["volume-type"] = volumeType.val();
                        changeBamSection("network");
                        console.log(bamInputs["volume-name"]);
                        console.log(bamInputs["volume-size"]);
                        console.log(bamInputs["volume-type"]);
                    }

                    break;

                case "network":

                    var networkInput = $('input[name=bam-select-network-input]:checked').val();

                    if (networkInput == "select") {

                        bamInputs["network-input"] = "select";
                        bamInputs["network-name"] = $("#bam-select-network-name").val();
                        changeBamSection("security");
                        console.log(bamInputs["network-input"]);
                        console.log(bamInputs["network-name"]);
                    }

                    if (networkInput == "create") {

                        var networkName = $("#bam-create-network-name"),
                            networkAdmin = $("#bam-create-network-admin-state"),
                            networkShared = $("#bam-create-network-shared"),
                            networkFields = $([]).add(networkName).add(networkAdmin).add(networkShared);

                        clearUiValidation(networkFields);

                        var isNetworkValid =
                            checkLength(networkName, "Network Name", 3, 16) &&
                            checkDuplicateName(networkName, privateNetworks);

                        if (isNetworkValid) {

                            bamInputs["network-input"] = "create";
                            bamInputs["network-name"] = networkName.val();
                            bamInputs["network-admin"] = networkAdmin.val();
                            bamInputs["network-shared"] = networkShared.val();
                            changeBamSection("security");
                            console.log(bamInputs["network-input"]);
                            console.log(bamInputs["network-name"]);
                            console.log(bamInputs["network-admin"]);
                            console.log(bamInputs["network-shared"]);
                        }

                    }

                    break;

                case "security":

                    var securityInput = $('input[name=bam-select-security-input]:checked').val();

                    if (securityInput == "select") {

                        bamInputs["security-input"] = "select";
                        bamInputs["security-name"] = $("#bam-select-security-name").val();
                        changeBamSection("confirm");
                        console.log(bamInputs["security-input"]);
                        console.log(bamInputs["security-name"]);
                    }

                    if (securityInput == "create") {

                        var securityName = $("#bam-create-security-name"),
                            securityDesc = $("#bam-create-security-description"),
                            securityTransport = $('input[name=bam-create-security-transport]:checked').val(),
                            securityPorts = $("#bam-create-security-ports"),
                            securityFields = $([]).add(securityName).add(securityDesc).add(securityTransport).add(securityPorts);

                        clearUiValidation(securityFields);

                        var isSecurityValid =
                            checkLength(securityName, "Security Group Name", 3, 16) &&
                            checkLength(securityName, "Security Group Name", 6, 80);

                        if (isSecurityValid) {

                            bamInputs["security-input"] = "create";
                            bamInputs["security-name"] = securityName.val();
                            bamInputs["security-description"] = securityDesc.val();
                            bamInputs["security-transport"] = securityTransport == undefined ? 'tcp' : securityTransport;
                            bamInputs["security-ports"] = securityPorts.val() == "" ? "443,80,22" : securityPorts.val();
                            changeBamSection("confirm");
                            console.log(bamInputs["security-input"]);
                            console.log(bamInputs["security-name"]);
                            console.log(bamInputs["security-description"]);
                            console.log(bamInputs["security-transport"]);
                            console.log(bamInputs["security-ports"]);
                        }

                    }

                    break;
            }
        });

        $("#bam-back-button").click(function (event) {

            event.preventDefault();

            switch (currentSection) {
                case "instance":
                    changeBamSection("instance");
                    break;
                case "key":
                    changeBamSection("instance");
                    break;
                case "volume":
                    changeBamSection("key");
                    break;
                case "network":
                    changeBamSection("volume");
                    break;
                case "security":
                    changeBamSection("network");
                    break;
                case "confirm":
                    changeBamSection("security");
                    break;
            }
        });

        $('input[name=bam-select-key-input]').change(function () {
            changeBamKeyInput();
        });

        $('input[name=bam-select-network-input]').change(function () {
            changeBamNetworkInput();
        });

        $('input[name=bam-select-security-input]').change(function () {
            changeBamSecurityInput();
        });
    });
});

var bamSections = { "instance": "#bam-instance-section", "key": "#bam-key-section", "volume": "#bam-volume-section", "network": "#bam-network-section", "security": "#bam-security-section" },
    currentSection = "instance";

var bamInputs = {
    "instance-name": "",
    "instance-image-input": "",
    "instance-image": "",
    "instance-flavor": "",
    "key": "",
    "volume-name": "",
    "volume-size": "",
    "volume-type": "",
    "network-input": "",
    "network-name": "",
    "network-admin": "",
    "network-shared": "",
    "security-input": "",
    "security-name": "",
    "security-description": "",
    "security-transport": "",
    "security-ports": ""
};

function initializeBamSection() {
    var form = $("#build-a-machine-form");
    currentSection = "instance";
    $("#bam-back-button").hide(0);
    form.dialog({ height: 318 });
    $("#bam-tips").html("Start by describing your virtual machine.");
    form.dialog("close");
}

function changeBamSection(toSection) {

    $(bamSections[currentSection]).hide(0);
    $(bamSections[toSection]).show(0);
    currentSection = toSection;

    var form = $("#build-a-machine-form"),
        next = $("#bam-next-button"),
        back = $("#bam-back-button"),
        tips = $("#bam-tips");

    switch (currentSection) {

        case "instance":
            back.hide(0);
            form.dialog({ height: 318 });
            tips.html("Start by describing your virtual machine.");
            break;

        case "key":
            back.show(0);
            form.dialog({ height: 262 });
            tips.html("Now select a pre-existing security key, or create a new one.");
            break;

        case "volume":
            form.dialog({ height: 333 });
            tips.html("Now create a volume to attach to the virtual machine.");
            break;

        case "network":
            form.dialog({ height: 333 });
            tips.html("Now select or create a network to use with the virtual machine.");
            break;

        case "security":
            form.dialog({ height: 358 });
            tips.html("Now select or create a security group for the virtual machine.");
            break;

        case "confirm":
            form.dialog({ height: 333 });
            tips.html("Here are the specifications for your new machine, you can go back to edit them or press confirm to create the machine.");
            break;
    }
}

function changeBamKeyInput() {
    var checked = $('input[name=bam-select-key-input]:checked').val();

    if (checked == 'select') {
        $("#bam-create-key-name").css("display", "none");
        $("#bam-create-key-label").css("display", "none");
        $("#bam-select-key-name").css("display", "inline-block");
        $("#bam-select-key-label").css("display", "block");
    }

    if (checked == 'create') {
        $("#bam-create-key-name").css("display", "inline-block");
        $("#bam-create-key-label").css("display", "block");
        $("#bam-select-key-name").css("display", "none");
        $("#bam-select-key-label").css("display", "none");
    }
}

function changeBamNetworkInput() {

    var checked = $('input[name=bam-select-network-input]:checked').val();

    console.log("net input changed");

    if (checked == 'select') {
        $("#bam-create-network-name").css("display", "none");
        $("#bam-create-network-name-label").css("display", "none");
        $("#bam-create-network-admin-state").css("display", "none");
        $("#bam-create-network-admin-label").css("display", "none");
        $("#bam-create-network-shared").css("display", "none");
        $("#bam-create-network-shared-label").css("display", "none");
        $("#bam-select-network-name").css("display", "inline-block");
        $("#bam-select-network-name-label").css("display", "block");
    }

    if (checked == 'create') {
        $("#bam-create-network-name").css("display", "inline-block");
        $("#bam-create-network-name-label").css("display", "block");
        $("#bam-create-network-admin-state").css("display", "inline-block");
        $("#bam-create-network-admin-label").css("display", "block");
        $("#bam-create-network-shared").css("display", "inline-block");
        $("#bam-create-network-shared-label").css("display", "block");
        $("#bam-select-network-name").css("display", "none");
        $("#bam-select-network-name-label").css("display", "none");
    }
}

function changeBamSecurityInput() {

    var checked = $('input[name=bam-select-security-input]:checked').val();

    console.log("net input changed");

    if (checked == 'select') {
        $("#bam-create-security-name").css("display", "none");
        $("#bam-create-security-name-label").css("display", "none");
        $("#bam-create-security-description").css("display", "none");
        $("#bam-create-security-description-label").css("display", "none");
        $("#bam-create-security-transport").css("display", "none");
        $("#bam-create-security-transport-label").css("display", "none");
        $("#bam-create-security-ports").css("display", "none");
        $("#bam-create-security-ports-label").css("display", "none");
        $("#bam-create-security-tcp").css("display", "none");
        $("#bam-create-security-tcp-label").css("display", "none");
        $("#bam-create-security-udp").css("display", "none");
        $("#bam-create-security-udp-label").css("display", "none");
        $("#bam-select-security-name").css("display", "inline-block");
        $("#bam-select-security-name-label").css("display", "block");
    }

    if (checked == 'create') {
        $("#bam-create-security-name").css("display", "inline-block");
        $("#bam-create-security-name-label").css("display", "block");
        $("#bam-create-security-description").css("display", "inline-block");
        $("#bam-create-security-description-label").css("display", "block");
        $("#bam-create-security-transport").css("display", "inline-block");
        $("#bam-create-security-transport-label").css("display", "block");
        $("#bam-create-security-ports").css("display", "inline-block");
        $("#bam-create-security-ports-label").css("display", "block");
        $("#bam-create-security-tcp").css("display", "inline-block");
        $("#bam-create-security-tcp-label").css("display", "inline-block");
        $("#bam-create-security-udp").css("display", "inline-block");
        $("#bam-create-security-udp-label").css("display", "inline-block");
        $("#bam-select-security-name").css("display", "none");
        $("#bam-select-security-name-label").css("display", "none");
    }
}