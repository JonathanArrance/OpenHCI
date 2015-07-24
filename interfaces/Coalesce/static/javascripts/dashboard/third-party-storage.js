$(function () {
    // Declare Page Container
    var page = $("#page-content");

    // Click Events
    // License
    $(document).on('click', '.license', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_storage/get_license/' + provider + '/';
        showModal(call);
    });

    $(document).on('click', '#confirm-license', function (event) {
        event.preventDefault();
        clearUiValidation();
        var provider = $(this).data("provider"),
            input = $("#license-input"),
            button = $(this),
            isValid = checkRequired(input, "License Key");

        if (isValid) {
            button.button('loading');
            button.prop("disabled", "disabled");
            showMessage('info', "Licensing Third Party Storage ...");
            var call = '/' + provider + '/license/set/' + input.val() + '/';

            $.getJSON(call)
                .done(function (data) {
                    if (data.status == 'error') {
                        showMessage('error', data.message);
                    }
                    if (data.status == 'success') {
                        showMessage('success', data.message);
                        refreshContent(page, "/third_party_storage/get/");
                        closeModal();
                    }
                })
                .fail(function () {
                    showMessage('error', 'Server Fault');
                })
                .always(function () {
                    button.button('reset');
                    button.removeProp("disabled");
                });
        }
    });

    // Configure and Update
    $(document).on('click', '.configure', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_storage/get_configure/' + provider + '/';
        showModal(call);
    });

    $(document).on('click', '.update', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_storage/get_configure/' + provider + '/true/';
        showModal(call);
    });

    $(document).on('click', '#confirm-configure', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            inputs,
            name,
            call,
            buttons = $(this).parent().parent().find('button'),
            isValid,
            notValidMsg,
            update = $(this).data("update");

        if (provider == "eseries") {
            inputs = {
                'useProxy': $('input[name=eseries-use-proxy]:checked'),
                'hostnameIP': $("#eseries-hostname-ip"),
                'login': $("#eseries-login"),
                'password': $("#eseries-password"),
                'controllerIPs': $("#eseries-mgmt-hostnames-ips"),
                'transport': $('input[name=eseries-transport]:checked'),
                'port': $("#eseries-server-port"),
                'disks': $("#eseries-storage-disk-pools"),
                'storagePassword': $("#eseries-storage-password")
            };
            name = "E-Series";
            isValid =
                (inputs.disks.find("option").length > 0) &&
                (inputs.disks.find("option:selected").length > 0);
            notValidMsg = "At least one Disk Pool must be selected to configure E-Series Storage";
        } else if (provider == "nfs") {
            inputs = $(".bootstrap-tagsinput").find('span.tag.label');
            name = "NFS";
            isValid = (inputs != "");
            notValidMsg = "At least one Mount Point must be entered to configure NFS Storage";
        } else if (provider == "nimble") {
            inputs = {
                'hostnameIP': $("#nimble-hostname-ip"),
                'login': $("#nimble-login"),
                'password': $("#nimble-password")
            };
            name = "Nimble";
            isValid =
                checkRequired(inputs.hostnameIP, "Hostname/IP") &&
                checkRequired(inputs.login, "Login") &&
                checkRequired(inputs.password, "Password");
            notValidMsg = "All fields are required to configure Nimble Storage";
        } else {
            isValid = false;
            showMessage("error", "Cannot determine storage provider");
            return;
        }

        if (isValid) {
            if (provider == "eseries") {
                call = update == true
                    ? 'eseries/config/update/' + configureEseriesUpdate(inputs) + '/'
                    : 'eseries/config/set/' + inputs.disks.val() + '/';
            } else if (provider == "nfs") {
                var mountpoints = "";
                $(inputs).each(function (index, element) {
                    mountpoints += element.textContent;
                    if (index + 1 != inputs.length) {
                        mountpoints += ",";
                    }
                });
                call = update == true
                    ? 'nfs/update/' + formatCall(mountpoints)
                    : 'nfs/set/' + formatCall(mountpoints);
            } else if (provider == "nimble") {
                call = update == true
                    ? 'nfs/update/' + configureNimble(inputs)
                    : 'nfs/set/' + configureNimble(inputs);
            }

            showMessage('info', update == true ? "Updating " + name + " Storage ..." : "Configuring " + name + " Storage ...");
            setModalButtons(false, buttons);
            $.getJSON(call)
                .done(function (data) {
                    if (data.status == 'error') {
                        if (data.message) {
                            showMessage('error', data.message);
                        } else if (data.msgs) {
                            // Hand NFS validation
                            $(inputs).each(function (index, element) {
                                $(element).removeClass('label-danger');
                            });
                            $(data.msgs).each(function (index, element) {
                                $(inputs).each(function (key, value) {
                                    if (value.textContent == element[0] && element[1] != "") {
                                        showMessage('error', "Error with " + element[0] + " " + element[1]);
                                        $(value).addClass('label-danger');
                                    }
                                });
                            });
                        }
                        setModalButtons(true, buttons);
                    }
                    if (data.status == 'success') {
                        showMessage('success', update == true ? name + " Storage Updated" : name + " Storage Configured");
                        setModalButtons(true, buttons);
                        closeModal();
                        refreshContent($("#page-content"), "/third_party_storage/get/");
                    }
                })
                .fail(function () {
                    showMessage('error', 'Server Fault');
                    setModalButtons(true, buttons);
                })
        } else {
            showMessage('warning', notValidMsg);
        }
    });

    $(document).on('click', '#eseries-discover-controllers', function (event) {
            event.preventDefault();
            clearUiValidation();
            var inputs = {
                    'useProxy': $("input[name='eseries-use-proxy']:checked"),
                    'hostnameIp': $("#eseries-hostname-ip"),
                    'login': $("#eseries-login"),
                    'password': $("#eseries-password"),
                    'transport': $("input[name='eseries-transport']:checked"),
                    'port': $("#eseries-server-port"),
                    'storagePassword': $("#eseries-storage-password")
                },
                buttons = $(this).parent().parent().find('button'),
                isValid =
                    checkRequired(inputs.hostnameIp, "Hostname/IP") &&
                    checkRequired(inputs.login, "Login") &&
                    checkRequired(inputs.password, "Password") &&
                    checkRequired(inputs.port, "Server Port") &&
                    checkRange(inputs.port, "Server Port", 0, 65535);

            if (isValid) {
                showMessage('info', "Discovering E-Series Storage Controllers ...");
                setModalButtons(false, buttons);
                var call =
                        '/eseries/web_proxy_srv/set/' +
                        inputs.useProxy.val() + '/' +
                        inputs.hostnameIp.val() + '/' +
                        inputs.port.val() + '/' +
                        inputs.transport.val() + '/' +
                        inputs.login.val() + '/' +
                        inputs.password.val() + '/',
                    size = 0,
                    controllers = $("#eseries-mgmt-hostnames-ips");
                $.getJSON(call)
                    .done(function (data) {
                        if (data.status == 'error') {
                            showMessage('error', data.message);
                            setModalButtons(true, buttons);
                            if ($("#eseries-mgmt-hostnames-ips option").length == 0) {
                                window.setTimeout(function () {
                                    $("#eseries-discover-disk-pools").prop("disabled", "disabled").css("cursor", "not-allowed!important");
                                }, 1);
                            }
                        }
                        if (data.status == 'success') {
                            showMessage('success', "Discovered Controllers");
                            controllers.empty();
                            for (var ip in data.ips) {
                                var option = '<option value="' + data.ips[ip] + '" selected>' + data.ips[ip] + '</option>';
                                controllers.append(option);
                                size++;
                            }

                            controllers.size = size;
                            controllers.removeProp("disabled");
                            setModalButtons(true, buttons);
                        }
                    })
                    .
                    fail(function () {
                        showMessage('error', 'Server Fault');
                        setModalButtons(true, buttons);
                        $("#eseries-discover-disk-pools").prop("disabled", "disabled").css("cursor", "not-allowed!important");
                    });
            }
        }
    );
    $(document).on('click', '#eseries-discover-disk-pools', function (event) {
        event.preventDefault();
        clearUiValidation();
        var inputs = {
                'password': $("#eseries-storage-password"),
                'hostnamesIPs': $("#eseries-mgmt-hostnames-ips")
            },
            buttons = $(this).parent().parent().find('button'),
            isValid =
                (inputs.hostnamesIPs.find('option').length > 0) &&
                (inputs.hostnamesIPs.find('option:selected').length > 0);

        if (isValid) {
            showMessage('info', "Discovering E-Series Disk Pools ...");
            setModalButtons(false, buttons);
            var call = inputs.password.val().length > 0
                    ? 'eseries/controller/set/' + inputs.hostnamesIPs.val() + '/' + inputs.password.val() + '/'
                    : 'eseries/controller/set/' + inputs.hostnamesIPs.val() + '/',
                size = 0,
                disks = $("#eseries-storage-disk-pools");

            $.getJSON(call)
                .done(function (data) {
                    if (data.status == 'error') {
                        showMessage('error', data.message);
                        setModalButtons(true, buttons);
                    }
                    if (data.status == 'success') {
                        showMessage('success', "Discovered Disk Pools");
                        for (var disk in data.pools) {
                            var option = '<option value="' + data.pools[disk].name + '" selected>' + data.pools[disk].name + ' (' + data.pools[disk].free + '/' + data.pools[disk].total + 'gb available)</option>';
                            disks.append(option);
                            size++;
                        }
                        disks.size = size;
                        disks.removeProp("disabled");
                        setModalButtons(true, buttons);
                    }
                })
                .fail(function () {
                    showMessage('error', 'Server Fault');
                    setModalButtons(true, buttons);
                })
        } else {
            showMessage('warning', "At least one Management Hostname/IP must be selected to discover Disk Pools");
        }
    });

    $(document).on('click', '.delete', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            title,
            message,
            call,
            notice,
            async = $(this).data("async");

        if (provider == "eseries") {
            title = formatSpaces("Delete E-Series Storage");
            message = formatSpaces("Remove E-Series Storage configuration");
            call = formatCall("/" + provider + "/delete/");
            notice = formatSpaces("Deleting E-Series Configuration");
            showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
        } else if (provider == "nfs") {
            title = formatSpaces("Delete NFS Storage");
            message = formatSpaces("Remove NFS Storage configuration");
            call = formatCall("/" + provider + "/delete/");
            notice = formatSpaces("Deleting NFS Configuration");
            showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
        }
    });

    $(document).on('keypress', '.tag-editable', function (e) {
        if (e.which == 13) {
            $(".bootstrap-tagsinput input").focus();
        }
    });
});

window.refreshTPS = (function (load) {
    $.when(load).done(function () {
        refreshContent($("#page-content"), "/third_party_storage/get/")
    });
});

function configureEseriesUpdate(inputs) {
    if (inputs.storagePassword.length > 0)
        return inputs.useProxy.val() + "/" + inputs.hostnameIP.val() + "/" + inputs.port.val() + "/" + inputs.transport.val() + "/" + inputs.login.val() + "/" + inputs.password.val() + "/" + inputs.controllerIPs.val() + "/" + inputs.disks.val() + "/" + inputs.storagePassword.val();
    else
        return inputs.useProxy.val() + "/" + inputs.hostnameIP.val() + "/" + inputs.port.val() + "/" + inputs.transport.val() + "/" + inputs.login.val() + "/" + inputs.password.val() + "/" + inputs.controllerIPs.val() + "/" + inputs.disks.val() + "/";
}

function configureNimble(inputs) {
    return inputs.hostnameIP.val() + "/" + inputs.login.val() + "/" + inputs.password.val();
}

window.getStorageStats = function() {
    window.loading.add("getStorageStats");
    var call = $.getJSON("/supported_third_party_storage/")
        .done(function (data) {
            $(data.providers).each(function (key, value) {
                if (value.configured == "1" && value.id == "eseries") {
                    var provider = value.id;
                    $.getJSON("/" + provider + "/get/stats/")
                        .done(function (stats) {
                            var pools = {};
                            $(stats.stats.data).each(function (index, element) {
                                if (pools[element.origin] === undefined) {
                                    pools[element.origin] = {};
                                }
                                pools[element.origin][element.volumeName] = element.usage
                            });
                            provider = "#" + provider;
                            for (var pool in pools) {
                                var poolData = [];
                                for (var datum in pools[pool]) {
                                    poolData.push([datum, pools[pool][datum]])
                                }
                                charts[pool].load({
                                    columns: poolData
                                });
                            }
                        });
                }
            });
        });
    window.loading.add("getStorageStats");
};

window.startDonutUpdateTimer = function() {
    if (window.gaugeTimer) {
        window.clearInterval(window.gaugeTimer);
    }
    window.gaugeTimer = setInterval(function () {
        getStorageStats();
    }, 30000)
};