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
            height: 350,
            width: 1060,
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

        $("#bam-create-button").click(function (event) {
            // TODO: IMPLEMENT create click event
        });

        $("#bam-cancel-button").click(function (event) {

            // TODO: IMPLEMENT cancel click event
        });

    });
});

var bamSections = {
        "instance": "#bam-instance-section",
        "key": "#bam-key-section",
        "volume": "#bam-volume-section",
        "network": "#bam-network-section",
        "security": "#bam-security-section"
    },
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
    $("#bam-cancel-button").hide(0);
    form.dialog({height: 318});
    $("#bam-tips").html("Start by describing your virtual machine.");
    form.dialog("close");
}

function changeBamSection(toSection) {

    $(bamSections[currentSection]).hide(0);
    $(bamSections[toSection]).show(0);
    currentSection = toSection;

    var form = $("#build-a-machine-form"),
        create = $("#bam-create-button"),
        cancel = $("#bam-cancel-button"),
        tips = $("#bam-tips");

    switch (currentSection) {

        case "instance":
            back.hide(0);
            form.dialog({height: 318});
            tips.html("Start by describing your virtual machine.");
            break;

        case "key":
            back.show(0);
            form.dialog({height: 262});
            tips.html("Now select a pre-existing security key, or create a new one.");
            break;

        case "volume":
            form.dialog({height: 333});
            tips.html("Now create a volume to attach to the virtual machine.");
            break;

        case "network":
            form.dialog({height: 333});
            tips.html("Now select or create a network to use with the virtual machine.");
            break;

        case "security":
            form.dialog({height: 358});
            tips.html("Now select or create a security group for the virtual machine.");
            break;

        case "confirm":
            form.dialog({height: 333});
            tips.html("Here are the specifications for your new machine, you can go back to edit them or press confirm to create the machine.");
            console.log("-------- USER INPUT OBJECT ---------");
            console.log(bamInputs);
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