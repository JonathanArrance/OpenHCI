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
        clearUiValidation();
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
            inputs = $("#nfs-mountpoints").val();
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
                call = update == true
                    ? 'nfs/update/' + formatCall(inputs)
                    : 'nfs/set/' + formatCall(inputs);
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
                        showMessage('error', data.message);
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
            title = formatString("Delete E-Series Storage");
            message = formatString("Remove E-Series Storage configuration");
            call = formatCall("/" + provider + "/delete/");
            notice = formatString("Deleting E-Series Configuration");
            showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
        } else if (provider == "nfs") {
            title = formatString("Delete NFS Storage");
            message = formatString("Remove NFS Storage configuration");
            call = formatCall("/" + provider + "/delete/");
            notice = formatString("Deleting NFS Configuration");
            showModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + async + '/');
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

function eseriesGraph() {
    d3.json("/eseries/get/stats/", function (error, json) {

        var m = 10, r = 75, z = d3.scale.category20c();

        var pie = d3.layout.pie()
            .value(function (d) {
                return +d.usage;
            })
            .sort(function (a, b) {
                return b.usage - a.usage;
            });

        var arc = d3.svg.arc()
            .innerRadius(r / 2)
            .outerRadius(r);

        var disks = d3.nest()
            .key(function (d) {
                return d.origin;
            })
            .entries(json.stats.data);

        var svg = d3.select("#graph").selectAll("div")
            .data(disks)
            .enter().append("div")
            .style("display", "inline-block")
            .style("width", (r + m) * 2 + "px")
            .style("height", (r + m) * 2 + "px")
            .append("svg:svg")
            .attr("width", (r + m) * 2)
            .attr("height", (r + m) * 2)
            .append("svg:g")
            .attr("transform", "translate(" + (r + m) + "," + (r + m) + ")");

        svg.append("svg:text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .text(function (d) {
                return d.key;
            });


        var g = svg.selectAll("g")
            .data(function (d) {
                return pie(d.values);
            })
            .enter().append("svg:g");

        g.append("svg:path")
            .attr("d", arc)
            .style("fill", function (d) {
                return z(d.data.volumeName);
            })
            .append("svg:title")
            .text(function (d) {
                return d.data.volumeName + ": " + d.data.usage;
            });

        g.filter(function (d) {
            return d.endAngle - d.startAngle > .2;
        }).append("svg:text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .attr("transform", function (d) {
                return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")";
            })
            .text(function (d) {
                return d.data.volumeName;
            });

        g.filter(function (d) {
            return d.endAngle - d.startAngle > .2;
        }).append("svg:text")
            .attr("dy", "15")
            .attr("text-anchor", "middle")
            .attr("transform", function (d) {
                return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")";
            })
            .text(function (d) {
                return d.data.usage;
            });
    });

    function angle(d) {
        var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
        return a > 90 ? a - 180 : a;
    }
}