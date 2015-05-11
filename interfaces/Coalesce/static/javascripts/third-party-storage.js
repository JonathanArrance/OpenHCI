$(function () {

    var eseries_configured,
        eseries_licensed,
        third_party_storage,
        mountpoints = {};

    // Form Elements
    var useExisting = $('input[name=eseries-use-existing]:checked').val(),
        hostnameIp = $("#eseries-hostname-ip"),
        login = $("#eseries-login"),
        password = $("#eseries-password"),
        transport = $('input[name=eseries-transport]:checked').val(),
        port = $("#eseries-server-port"),
        controllerPassword = $("#eseries-storage-controller-password"),
        controllers = $("#eseries-mgmt-hostnames-ips"),
        disks = $("#eseries-storage-disk-pools"),
        allFields = $([]).add(useExisting).add(hostnameIp).add(login).add(password).add(port).add(controllerPassword).add(controllers).add(disks);

    // Local Variables
    var controllerIps = [],
        diskPools = [];

    // On page load
    $(function () {
        refreshTps();
        updateEseriesTransport(transport);
    });

    $('input[name=eseries-transport]').change(function () {
        updateEseriesTransport($('input[name=eseries-transport]:checked').val());
    });

    $("#config-third-party-storage").click(function (event) {

        // Prevent scrolling to top of page on click
        event.preventDefault();

        $("#tps-table-container").empty();
        $("#tps-config-form").dialog({height: 210}).dialog("open");
        $("#tps-form-legend").html("Third Party Storage");

        var loader1 = $("#tps-loader-1");
        loader1.show();
        refreshTps();
        buildTpsTable();
        loader1.hide();
    });

    $("#add-mountpoint").click(function () {

        var input = $("#nfs-mountpoint").val().toString();
        addMountpoint(input);
    });

    $(document).on("click", ".remove-mountpoint", function () {

        var index = $(this).closest(".mountpoint").attr('id');
        mountpoints[index] = undefined;
        $(this).closest(".mountpoint").fadeOut();
    });

    $(".configure-tps").on('click', function () {

        var provider = $(this).data("provider"),
            config3ps,
            isValid = false;


        // Remove UI validation flags
        clearUiValidation(allFields);

        if (provider == 'eseries') {
            if (diskPools.length > 0) {
                isValid = true;
                config3ps = $.getJSON('eseries/config/set/' + diskPools + '/');
            }
        }

        if (provider == 'nfs') {
            var params = configureMountpoints();
            if (params != "") {
                isValid = true;
                config3ps = $.getJSON('nfs/set/' + configureMountpoints() + '/');
            }
        }

        if (isValid) {
            config3ps
                .done(function (data) {

                    if (data.status == "error") {

                        message.showMessage("error", data.message);
                    }

                    if (data.status == "success") {

                        message.showMessage("success", data.message);

                        hideFields();
                        $("#tps-config-form").dialog("close");
                        refreshTps();
                    }

                })
                .fail(function () {

                    message.showMessage("error", "Server Fault");
                })
        }
    });

    $("#confirm-license").on("click", function () {

        var licenseNo = $("#eseries-license-no").val();

        $.getJSON('/eseries/license/set/' + licenseNo + '/')
            .done(function (data) {

                refreshTps();

                $("#license-eseries").replaceWith('<a href="#" id="configure-eseries">configure</a>');
                $("#eseries-license-confirmation").hide();

                var configId = "#configure-eseries";
                $(configId).bind("click", function (event) {

                    event.preventDefault();
                    $("#eseries-web-proxy-server-data").show();
                });

            })
            .fail(function () {

                message.showMessage("error", "Server Fault");
            })
    });

    $("#eseries-discover-controllers").click(function (event) {

        event.preventDefault();
        controllers.empty();
        clearUiValidation(allFields);

        var isValid =
            checkRequired($("#eseries-hostname-ip"), "Hostname/IP") &&
            checkRequired($("#eseries-login"), "Login") &&
            checkRequired($("#eseries-password"), "Password") &&
            checkRange($("#eseries-server-port"), "Server Port", 80, 65535);

        // Confirmed Selections
        var confUseExisting = $('input[name=eseries-use-existing]:checked').val(),
            confHostnameIp = $("#eseries-hostname-ip").val(),
            confLogin = $("#eseries-login").val(),
            confPassword = $("#eseries-password").val(),
            confTransport = $('input[name=eseries-transport]:checked').val(),
            confPort = $("#eseries-server-port").val();

        if (isValid) {

            disableLink("#eseries-discover-controllers", true);
            $("#tps-loader-2").show();

            $.getJSON('/eseries/web_proxy_srv/set/' + confUseExisting + '/' + confHostnameIp + '/' + confPort + '/' + confTransport + '/' + confLogin + '/' + confPassword + '/')
                .done(function (data) {

                    if (data.status == "error") {

                        message.showMessage("error", data.message);
                    }

                    if (data.status == "success") {

                        var size = 0;

                        for (var ip in data.ips) {
                            var option = '<option value="' + data.ips[ip] + '" selected>' + data.ips[ip] + '</option>';
                            controllers.append(option);
                            controllerIps.push(data.ips[ip]);
                            size++;
                        }

                        controllers.size = size;

                        $("#eseries-web-proxy-server-data").hide();
                        $("#tps-config-form").dialog({height: 285});
                        $("#eseries-storage-controller-data").show();
                    }
                })
                .fail(function () {

                    message.showMessage("error", "Server Fault");
                })
                .always(function () {

                    disableLink("#eseries-discover-controllers", false);
                    $("#tps-loader-2").hide();
                });
        }
    });

    $("#eseries-discover-disk-pools").click(function (event) {

        event.preventDefault();

        $("#eseries-storage-controller-data").hide();
        $("#tps-config-form").dialog({height: 260});
        disableLink("#eseries-discover-disk-pools", true);

        // Confirmed Selections
        var confControllerPassword = $("#eseries-storage-controller-password").val();
        var url;

        url = confControllerPassword.length > 0
            ? 'eseries/controller/set/' + confControllerPassword + '/' + controllerIps + '/'
            : 'eseries/controller/set/' + controllerIps + '/';

        $.getJSON(url)
            .done(function (data) {

                if (data.status == "error") {

                    message.showMessage("error", data.message);
                }

                if (data.status == "success") {
                    var size = 0;

                    for (var disk in data.pools) {
                        var option = '<option value="' + data.pools[disk] + '" selected>' + data.pools[disk].name + ' (' + data.pools[disk].free + '/' + data.pools[disk].total + 'gb available)</option>';
                        disks.append(option);
                        diskPools.push(data.pools[disk].name);
                        size++;
                    }

                    disks.size = size;
                }

                $("#eseries-disk-pools").show();
            })
            .fail(function () {

                message.showMessage("error", "Server Fault");
            })
            .always(function () {

                disableLink("#eseries-discover-disk-pools", false);
                $("#tps-loader-2").hide();
            });
    });

    $("#tps-config-form").dialog({
        autoOpen: false,
        height: 210,
        width: 300,
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
            "Cancel": function () {

                // Reset form validation
                hideFields();
                $("#tps-config-form").dialog("close");
            }
        }
    });

    function hideFields() {
        resetUiValidation(allFields);
        $("#tps-config-form fieldset").each(function () {
            if ($(this).attr('id') != "tps-form") {
                $(this).hide();
            }
        });
    }

    function buildTpsTable() {

        var configTable = '<table class="paleblue widget-table" id="tps-table"><tr><th>Name</th><th>Configured</th><th>Actions</th></tr></table>';
        $("#tps-table-container").append(configTable);

        for (var i = 0; i < third_party_storage.providers.length; i++) {

            var provider = third_party_storage.providers[i];
            var newRow = '<tr id="' + provider.id + '"><td>' + provider.name + '</td>';

            if (provider.configured == 0) {
                newRow += provider.id == 'eseries' && eseries_licensed != true
                    ? '<td>No</td><td><a href="#" id="license-' + provider.id + '">license</a></td>'
                    : '<td>No</td><td><a href="#" id="configure-' + provider.id + '">configure</a></td>';
            }

            if (provider.configured == 1) {
                newRow += '<td>Yes</td><td><a href="#" id="delete-' + provider.id + '">delete</a></td>';
            }

            newRow += '</tr>';

            $("#tps-table").append(newRow);

            if (provider.id == "eseries") {

                var configId = "#configure-eseries";
                $(configId).bind("click", function (event) {

                    event.preventDefault();
                    hideFields();
                    updateEseriesTransport();
                    $("#tps-table").hide();
                    $("#tps-config-form").dialog({height: 535});
                    $("#tps-form-legend").html("NetApp E-Series");
                    $("#eseries-web-proxy-server-data").show();
                });

                var licenseConfirm = "#license-eseries";
                $(licenseConfirm).bind("click", function (event) {

                    event.preventDefault();
                    hideFields();
                    $("#eseries-license-confirmation").show();
                });

                var deleteId = "#delete-eseries";
                $(deleteId).bind("click", function (event) {

                    event.preventDefault();
                    deleteTps("eseries");
                });
            }

            if (provider.id == "nfs") {

                var configId = "#configure-nfs";
                $(configId).bind("click", function (event) {

                    event.preventDefault();
                    hideFields();
                    $("#tps-table").hide();
                    $("#tps-config-form").dialog({height: 360});
                    $("#tps-form-legend").html("NFS");
                    $("#nfs-web-proxy-server-data").show();
                });

                var deleteId = "#delete-nfs";
                $(deleteId).bind("click", function (event) {

                    event.preventDefault();
                    deleteTps("nfs");
                });
            }
        }
    }

    function deleteTps(provider) {

        var url = "/" + provider + "/delete/";

        $.getJSON(url)
            .done(function (data) {

                if (data.status == "error") {

                    message.showMessage("error", data.message);
                }

                if (data.status == "success") {

                    message.showMessage("success", data.message);
                    refreshTps();
                }
            })
            .fail(function () {

                message.showMessage("error", "Server Fault");
            })
            .always(function () {
                hideFields();
                $("#tps-config-form").dialog("close");
            });
    }

    function addMountpoint(mountpoint) {

        var index = "mp" + Object.keys(mountpoints).length;
        var mp = {
            "index": index,
            "mountpoint": mountpoint,
            "html": '<div id="' + index + '" class="mountpoint"><span class="mountpoint-text">' + mountpoint + '</span><button class="remove-mountpoint">-</button></div>'
        };
        mountpoints[index] = mp;
        $("#mountpoints").append($(mp.html).fadeIn());
    }

    function configureMountpoints() {

        var keys = Object.keys(mountpoints),
            validKeys = [],
            paramString = "";

        for (var i = 0; i < keys.length; i++) {
            if (mountpoints[keys[i]] != undefined) {
                validKeys[validKeys.length] = mountpoints[keys[i]];
            }
        }

        for (var j = 0; j < validKeys.length; j++) {
            var mountString = validKeys[j].mountpoint.toString();
            for (var k = 0; k < mountString.length; k++) {
                if (mountString[k] === '/') {
                    mountString = mountString.replace('/', '!');
                }
            }

            paramString += mountString;

            if (j + 1 != validKeys.length) {
                paramString += ",";
            }
        }

        return paramString;
    }

    function refreshTps() {

        $.getJSON('/supported_third_party_storage/')
            .done(function (data) {

                data.providers.forEach(function (provider) {
                    if (provider.id == "eseries") {
                        eseries_configured = !(provider.configured == 0);
                        eseries_licensed = (provider.licensed == 1);

                        if (eseries_configured) {
                            $("#graph-placeholder").hide();
                            $("#graph-title").html("E-Series Storage (gb)");
                            $("#graph").html(TpsGraph()).show();
                        } else {
                            $("#graph-title").html("E-Series Storage (gb) (Not Configured)");
                            $("#graph").hide();
                        }
                    }
                });

                third_party_storage = {'status': data.status, 'providers': data.providers};
            })
            .fail(function (data) {

                message.showMessage('error', data.message);

                var retry = '<p>Error getting supported 3rd Party Storage, <span><a href="#" id="retry">Retry?</a></span></p>';
                $("#tps-table-container").append(retry);

                third_party_storage = {'status': data.status};
            });
    }

    function updateEseriesTransport(checked) {

        if (checked == 'http') {
            $("#eseries-server-port").val("8080");
        } else if (checked == 'https') {
            $("#eseries-server-port").val("8443");
        } else {
            $('input[id=http]').prop('checked', true);
            $("#eseries-server-port").val("8080");
        }
    }

    function TpsGraph() {

        var url = "/eseries/get/stats/";

        d3.json(url, function (error, json) {

            var m = 10, r = 100, z = d3.scale.category20c();

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
});