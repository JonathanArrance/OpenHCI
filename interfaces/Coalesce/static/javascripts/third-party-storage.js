$(function ()
{
    var ESERIES_ID = "",
        ESERIES_NAME = "",
        ESERIES_CONFIG_WIDTH = 290,
        ESERIES_CONFIG_HEIGHT = 530;

    var ESERIES_CONTROLLER_DATA_WIDTH = 290,
        ESERIES_CONTROLLER_DATA_HEIGHT = 290;

    var ESERIES_DISK_POOLS_WIDTH = 350,
        ESERIES_DISK_POOLS_HEIGHT = 279;

    var NFS_ID = "",
        NFS_NAME = "",
        NFS_CONFIG_WIDTH = 330,
        NFS_CONFIG_HEIGHT = 350;

    var NIMBLE_ID = "",
        NIMBLE_NAME = "",
        NIMBLE_CONFIG_WIDTH = 290,
        NIMBLE_CONFIG_HEIGHT = 360;

    var TPS_FORM_WIDTH = 420,
        TPS_FORM_HEIGHT = 228;

    var LICENSE_WIDTH = 300,
        LICENSE_HEIGHT = 250;

    var third_party_storage,
        current_provider_id = "",
        close_tps_form = true,
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
        license = $("#license-num"),
        nimhost = $("#nimble-hostname-ip"),
        nimlogin = $("#nimble-login"),
        nimpwd = $("#nimble-password"),
        mntpt = $("#nfs-mountpoint"),
        mntpts = $("#mountpoints"),
        allFields = $([]).add(useExisting).add(hostnameIp).add(login).add(password).add(port).add(controllerPassword).add(controllers).add(disks).add(license).add(nimhost).add(nimlogin).add(nimpwd).add(mntpt).add(mntpts);

    // Local Variables
    var controllerIps = [],
        diskPools = [];

    // On page load
    $(function ()
    {
        refreshTps();
        updateEseriesTransport(transport);
    });

    $('input[name=eseries-transport]').change(function ()
    {
        updateEseriesTransport($('input[name=eseries-transport]:checked').val());
    });

    $("#config-third-party-storage").click(function (event)
    {
        // Prevent scrolling to top of page on click
        event.preventDefault();
        buildTpsDialog();
    });

    $("#add-mountpoint").click(function ()
    {
        var input = $("#nfs-mountpoint").val().toString();
        addMountpoint(input);
    });

    $(document).on("click", ".remove-mountpoint", function ()
    {
        var index = $(this).closest(".mountpoint").attr('id');
        //mountpoints[index] = undefined;
        delete mountpoints[index];
        $(this).closest(".mountpoint").fadeOut();
        $("#" + index).remove();
    });

    $(".configure-tps").on('click', function ()
    {
        var provider = $(this).data("provider"),
            config3ps,
            configure = true,
            isValid = false;

        // Remove UI validation flags
        clearUiValidation(allFields);

        for (var i = 0; i < third_party_storage.providers.length; i++)
        {
            var prov = third_party_storage.providers[i];
            if (prov.id == provider)
            {
                if (prov.configured == 0)
                    configure = true;
                else
                    configure = false;
                break;
            }
        }

        if (provider == 'eseries')
        {
            if (diskPools.length > 0)
            {
                isValid = true;
                if (configure)
                    config3ps = $.getJSON('eseries/config/set/' + diskPools + '/');
                else
                    config3ps = $.getJSON('eseries/config/update/' + configureEseries() + '/');
            }
        }

        else if (provider == 'nfs')
        {
            var params = configureMountpoints();
            if (params != "")
            {
                isValid = true;
                if (configure)
                    config3ps = $.getJSON('nfs/set/' + params + '/');
                else
                    config3ps = $.getJSON('nfs/update/' + params + '/');
            }
        }

        else if (provider == 'nimble')
        {
            var params = configureNimble();
            if (params != "")
            {
                isValid = true;
                if (configure)
                    config3ps = $.getJSON('nimble/set/' + params + '/');
                else
                    config3ps = $.getJSON('nimble/update/' + params + '/');
            }
        }

        if (isValid)
        {
            config3ps
                .done(function (data)
                {
                    if (data.status == "success")
                    {
                        message.showMessage("success", data.message);

                        hideFields();
                        $("#tps-config-form").dialog("close");
                    }

                    else if (data.status == "error")
                    {
                        message.showMessage("error", data.message);
                    }
                })
                .fail(function ()
                {
                    message.showMessage("error", "Server Fault");
                })
        }
    });

    $("#eseries-discover-controllers").click(function (event)
    {
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

        if (isValid)
        {
            disableLink("#eseries-discover-controllers", true);
            $("#tps-loader-2").show();

            $.getJSON('/eseries/web_proxy_srv/set/' + confUseExisting + '/' + confHostnameIp + '/' + confPort + '/' + confTransport + '/' + confLogin + '/' + confPassword + '/')
                .done(function (data)
                {
                    if (data.status == "success")
                    {
                        var size = 0;

                        for (var ip in data.ips)
                        {
                            var option = '<option value="' + data.ips[ip] + '" selected>' + data.ips[ip] + '</option>';
                            controllers.append(option);
                            controllerIps.push(data.ips[ip]);
                            size++;
                        }

                        controllers.size = size;

                        $("#eseries-config-data").hide();
                        $("#tps-config-form").dialog({ height: ESERIES_CONTROLLER_DATA_HEIGHT, width: ESERIES_CONTROLLER_DATA_WIDTH });
                        $("#eseries-storage-controller-data").show();
                    }

                    else if (data.status == "error")
                    {
                        message.showMessage("error", data.message);
                    }
                })
                .fail(function ()
                {
                    message.showMessage("error", "Server Fault");
                })
                .always(function ()
                {
                    disableLink("#eseries-discover-controllers", false);
                    $("#tps-loader-2").hide();
                });
        }
    });

    $("#eseries-discover-disk-pools").click(function (event)
    {
        event.preventDefault();

        $("#eseries-storage-controller-data").hide();
        $("#tps-config-form").dialog({ height: ESERIES_DISK_POOLS_HEIGHT, width: ESERIES_DISK_POOLS_WIDTH });
        disableLink("#eseries-discover-disk-pools", true);

        // Confirmed Selections
        var confControllerPassword = $("#eseries-storage-controller-password").val();

        var url;
        if (confControllerPassword.length > 0)
            url = 'eseries/controller/set/' + controllerIps + '/' + confControllerPassword + '/';
        else
            url = 'eseries/controller/set/' + controllerIps + '/';

        $.getJSON(url)
            .done(function (data)
            {
                if (data.status == "success")
                {
                    var size = 0;

                    for (var disk in data.pools)
                    {
                        var option = '<option value="' + data.pools[disk] + '" selected>' + data.pools[disk].name + ' (' + data.pools[disk].free + '/' + data.pools[disk].total + 'gb available)</option>';
                        disks.append(option);
                        diskPools.push(data.pools[disk].name);
                        size++;
                    }
                    disks.size = size;
                }

                else if (data.status == "error")
                {
                    message.showMessage("error", data.message);
                }

                $("#eseries-disk-pools").show();
            })
            .fail(function ()
            {
                message.showMessage("error", "Server Fault");
            })
            .always(function ()
            {
                disableLink("#eseries-discover-disk-pools", false);
                $("#tps-loader-2").hide();
            });
    });

    $("#tps-config-form").dialog(
    {
        autoOpen: false,
        height: TPS_FORM_HEIGHT,
        width: TPS_FORM_WIDTH,
        modal: true,
        resizable: true,
        closeOnEscape: true,
        draggable: true,
        show: "fade",
        position: {
            my: "center",
            at: "center",
            of: $('#page-content')
        },
        buttons:
        {
            "Cancel": function ()
            {
                if (close_tps_form)
                {
                    // Reset form validation
                    hideFields();
                    $("#tps-config-form").dialog("close");
                }
                else
                {
                    hideFields();
                    buildTpsDialog();
                }
            }
        }
    });

    $("#license-apply").click(function (event)
    {
        var isValid = checkRequired($("#license-num"), "License Key");

        if (isValid)
        {
            var licenseNum = $("#license-num").val();

            $.getJSON('/' + current_provider_id + '/license/set/' + licenseNum + '/')
            .done(function (data)
            {
                if (data.status == "success")
                {
                    message.showMessage("success", data.message);
                    hideFields();
                    buildTpsDialog();
                }

                else if (data.status == "error")
                {
                    message.showMessage("error", data.message);
                }
            })
            .fail(function ()
            {
                message.showMessage("error", "Server Fault");
            })
        }
        return;
    });

    function hideFields()
    {
        var keys = Object.keys(mountpoints);
        for (var i = 0; i < keys.length; i++)
        {
            $("#mp" + i).remove();
        }
        mountpoints = {};

        resetUiValidation(allFields);
        $("#tps-config-form fieldset").each(function ()
        {
            if ($(this).attr('id') != "tps-form")
            {
                $(this).hide();
            }
        });
    }

    function buildTpsDialog()
    {
        $("#tps-table-container").empty();
        $("#tps-config-form").dialog({ height: TPS_FORM_HEIGHT, width: TPS_FORM_WIDTH }).dialog("open");
        $("#tps-form-legend").html("Third Party Storage");

        close_tps_form = true;

        var loader1 = $("#tps-loader-1");
        loader1.show();
        refreshTps();
        loader1.hide();
        return;
    }

    function buildTpsTable()
    {
        var configTable = '<table class="paleblue widget-table" id="tps-table"><tr><th>Name</th><th>Status</th><th>Actions</th></tr></table>';
        $("#tps-table-container").append(configTable);

        for (var i = 0; i < third_party_storage.providers.length; i++)
        {
            var provider = third_party_storage.providers[i];
            var newRow = '<tr id="' + provider.id + '"><td>' + provider.name + '</td>';

            if (provider.configured == 0 && provider.licensed == 0)
                newRow += '<td>Unlicensed</td><td><a href="#" id="license-' + provider.id + '">license</a></td>';
            else if (provider.configured == 0 && provider.licensed == 1)
                newRow += '<td>Unconfigured</td><td><a href="#" id="configure-' + provider.id + '">configure</a></td>';
            else if (provider.in_use == 0)
                newRow += '<td>Configured - no volumes</td><td><a href="#" id="update-' + provider.id + '">update</a> <a href="#" id="delete-' + provider.id + '">delete</a></td>';
            else
                newRow += '<td>Configured - with volumes</td><td><a href="#" id="update-' + provider.id + '">update</a></td>';

            newRow += '</tr>';

            $("#tps-table").append(newRow);

            if (provider.id == "eseries")
            {
                ESERIES_ID = provider.id;
                ESERIES_NAME = provider.name;

                buildConfigure(ESERIES_ID, ESERIES_NAME, ESERIES_CONFIG_WIDTH, ESERIES_CONFIG_HEIGHT);
                buildLicense(ESERIES_ID, ESERIES_NAME);
                buildUpdate(ESERIES_ID, ESERIES_NAME, ESERIES_CONFIG_WIDTH, ESERIES_CONFIG_HEIGHT);
                deleteConfigure(ESERIES_ID, ESERIES_NAME);
            }

            else if (provider.id == "nfs")
            {
                NFS_ID = provider.id;
                NFS_NAME = provider.name;

                buildConfigure(NFS_ID, NFS_NAME, NFS_CONFIG_WIDTH, NFS_CONFIG_HEIGHT);
                buildLicense(NFS_ID, NFS_NAME);
                buildUpdate(NFS_ID, NFS_NAME, NFS_CONFIG_WIDTH, NFS_CONFIG_HEIGHT);
                deleteConfigure(NFS_ID, NFS_NAME);
            }

            else if (provider.id == "nimble")
            {
                NIMBLE_ID = provider.id;
                NIMBLE_NAME = provider.name;

                buildConfigure(NIMBLE_ID, NIMBLE_NAME, NIMBLE_CONFIG_WIDTH, NIMBLE_CONFIG_HEIGHT);
                buildLicense(NIMBLE_ID, NIMBLE_NAME);
                buildUpdate(NIMBLE_ID, NIMBLE_NAME, NIMBLE_CONFIG_WIDTH, NIMBLE_CONFIG_HEIGHT);
                deleteConfigure(NIMBLE_ID, NIMBLE_NAME);
            }
        }
    }

    function buildConfigureDetails(id, name, dialog_wd, dialog_ht, event)
    {

        var prov_name = name;
        close_tps_form = false;
        if (event != undefined)
            event.preventDefault();
        $("#tps-table").hide();
        $("#tps-config-form").dialog({ height: dialog_ht, width: dialog_wd });
        $("#tps-form-legend").html(prov_name);
        $("#" + id + "-config-data").show();
        return;
    }

    function buildConfigure(id, name, dialog_wd, dialog_ht)
    {
        var configId = "#configure-" + id;
        $(configId).bind("click", function (event)
        {
            buildConfigureDetails(id, name, dialog_wd, dialog_ht, event)
        });
        return;
    }

    function buildUpdate(id, name, dialog_wd, dialog_ht)
    {
        var updateId = "#update-" + id;
        $(updateId).bind("click", function (event)
        {
            close_tps_form = false;
            event.preventDefault();
            updateTps(id, name, dialog_wd, dialog_ht);
        });
        return;
    }

    function deleteConfigure(id, name)
    {
        var prov_name = name;
        var deleteId = "#delete-" + id;
        $(deleteId).bind("click", function (event)
        {
            close_tps_form = false;
            event.preventDefault();
            deleteTps(id);
        });
        return;
    }

    function buildLicense(id, name)
    {
        var prov_name = name + " License";
        var licenseConfirm = "#license-" + id;
        $(licenseConfirm).bind("click", function (event)
        {
            close_tps_form = false;
            current_provider_id = id;
            event.preventDefault();
            hideFields();
            $("#tps-table").hide();
            $("#tps-config-form").dialog({ height: LICENSE_HEIGHT, width: LICENSE_WIDTH });
            $("#tps-form-legend").html(prov_name);
            $("#license-confirm").show();
        });
        return;
    }

    function updateTps(id, name, dialog_wd, dialog_ht)
    {
        var url = "/" + id + "/get/";

        $.getJSON(url)
            .done(function (ret_data)
            {
                if (ret_data.status == "success")
                {
                    if (id == "nfs")
                    {
                        $.each(ret_data.data.mountpoint, function (mp)
                        {
                            addMountpoint(ret_data.data.mountpoint[mp]);
                        });
                        $("#nfs-button").html("Update " + name);
                    }

                    else if (id == "eseries")
                    {
                        $("#eseries-hostname-ip").val(ret_data.data.server);
                        $("#eseries-server-port").val(ret_data.data.srv_port);
                        $("#eseries-login").val(ret_data.data.login);
                        $("#eseries-password").val(ret_data.data.pwd);
                        $("#eseries-storage-controller-password").val(ret_data.data.ctrl_pwd);

                        if (ret_data.data.transport == "http")
                            $('input[id=http]').prop('checked', true);
                        else
                            $('input[id=https]').prop('checked', true);
                        $("#eseries-button").html("Update " + name);
                    }

                    else if (id == "nimble")
                    {
                        $("#nimble-hostname-ip").val(ret_data.data.server);
                        $("#nimble-login").val(ret_data.data.login);
                        $("#nimble-password").val(ret_data.data.pwd);
                        $("#nimble-button").html("Update " + name);
                    }

                    buildConfigureDetails(id, name, dialog_wd, dialog_ht)
                }

                else if (ret_data.status == "error")
                {
                    message.showMessage("error", ret_data.message);
                }
            })
            .fail(function ()
            {
                message.showMessage("error", "Server Fault");
            })
        return;
    }

    function deleteTps(provider)
    {
        var url = "/" + provider + "/delete/";

        $.getJSON(url)
            .done(function (data)
            {
                if (data.status == "error")
                {
                    message.showMessage("error", data.message);
                }

                if (data.status == "success")
                {
                    message.showMessage("success", data.message);
                }
            })
            .fail(function ()
            {
                message.showMessage("error", "Server Fault");
            })
            .always(function ()
            {
                hideFields();
                buildTpsDialog();
                //$("#tps-config-form").dialog("close");
            });
    }

    function addMountpoint(mountpoint)
    {
        var index = "mp" + Object.keys(mountpoints).length;
        if ($("#" + index).length == 0)
        {
            var mp = {
                "index": index,
                "mountpoint": mountpoint,
                "html": '<div id="' + index + '" class="mountpoint"><span class="mountpoint-text">' + mountpoint + '</span><button class="remove-mountpoint">-</button></div>'
            };
            mountpoints[index] = mp;
            $("#mountpoints").append($(mp.html).fadeIn());
        }
    }

    function configureEseries()
    {
        var confUseExisting = $('input[name=eseries-use-existing]:checked').val(),
            confHostnameIp = $("#eseries-hostname-ip").val(),
            confLogin = $("#eseries-login").val(),
            confPassword = $("#eseries-password").val(),
            confTransport = $('input[name=eseries-transport]:checked').val(),
            confPort = $("#eseries-server-port").val(),
            confControllerPassword = $("#eseries-storage-controller-password").val();

        if (confControllerPassword.length > 0)
            retString = confUseExisting + "/" + confHostnameIp + "/" + confPort + "/" + confTransport + "/" + confLogin + "/" + confPassword + "/" + controllerIps + "/" + diskPools + "/" + confControllerPassword;
        else
            retString = confUseExisting + "/" + confHostnameIp + "/" + confPort + "/" + confTransport + "/" + confLogin + "/" + confPassword + "/" + controllerIps + "/" + diskPools;
        return (retString);
    }

    function configureMountpoints()
    {
        var keys = Object.keys(mountpoints),
            validKeys = [],
            paramString = "";

        for (var i = 0; i < keys.length; i++)
        {
            validKeys[validKeys.length] = mountpoints[keys[i]];
        }

        for (var j = 0; j < validKeys.length; j++)
        {
            var mountString = validKeys[j].mountpoint.toString();
            for (var k = 0; k < mountString.length; k++)
            {
                if (mountString[k] === '/')
                {
                    mountString = mountString.replace('/', '!');
                }
            }

            paramString += mountString;

            if (j + 1 != validKeys.length)
            {
                paramString += ",";
            }
        }

        $(".mountpoints").empty();
        //mountpoints = {};

        return paramString;
    }

    function configureNimble()
    {
        var isValid =
        checkRequired($("#nimble-hostname-ip"), "Hostname/IP") &&
        checkRequired($("#nimble-login"), "Login") &&
        checkRequired($("#nimble-password"), "Password");

        if (!isValid)
            return ("");

        // Confirmed Selections
        var confHostnameIp = $("#nimble-hostname-ip").val(),
        confLogin = $("#nimble-login").val(),
        confPassword = $("#nimble-password").val();

        retString = confHostnameIp + "/" + confLogin + "/" + confPassword;
        return (retString);
    }

    function refreshTps()
    {
        $.getJSON('/supported_third_party_storage/')
            .done(function (data)
            {
                data.providers.forEach(function (provider)
                {
                    if (provider.id == "eseries")
                    {
                        if (provider.configured == 1)
                        {
                            $("#graph-placeholder").hide();
                            $("#graph-title").html("E-Series Storage (GB)");
                            $("#graph").html(TpsGraph()).show();
                        }
                        else
                        {
                            $("#graph-title").html("E-Series Storage (Not Configured)");
                            $("#graph").hide();
                        }
                    }
                });

                third_party_storage = { 'status': data.status, 'providers': data.providers };
                buildTpsTable();
            })
            .fail(function (data)
            {
                message.showMessage('error', data.message);

                var retry = '<p>Error getting supported 3rd Party Storage, <span><a href="#" id="retry">Retry?</a></span></p>';
                $("#tps-table-container").append(retry);

                third_party_storage = { 'status': data.status };
            });
    }

    function updateEseriesTransport(checked)
    {
        if (checked == 'http')
        {
            $("#eseries-server-port").val("8080");
        }
        else if (checked == 'https')
        {
            $("#eseries-server-port").val("8443");
        }
        else
        {
            $('input[id=http]').prop('checked', true);
            $("#eseries-server-port").val("8080");
        }
    }

    function TpsGraph()
    {
        var url = "/eseries/get/stats/";

        d3.json(url, function (error, json)
        {

            var m = 10, r = 75, z = d3.scale.category20c();

            var pie = d3.layout.pie()
                .value(function (d)
                {
                    return +d.usage;
                })
                .sort(function (a, b)
                {
                    return b.usage - a.usage;
                });

            var arc = d3.svg.arc()
                .innerRadius(r / 2)
                .outerRadius(r);

            var disks = d3.nest()
                .key(function (d)
                {
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
                .text(function (d)
                {
                    return d.key;
                });


            var g = svg.selectAll("g")
                .data(function (d)
                {
                    return pie(d.values);
                })
                .enter().append("svg:g");

            g.append("svg:path")
                .attr("d", arc)
                .style("fill", function (d)
                {
                    return z(d.data.volumeName);
                })
                .append("svg:title")
                .text(function (d)
                {
                    return d.data.volumeName + ": " + d.data.usage;
                });

            g.filter(function (d)
            {
                return d.endAngle - d.startAngle > .2;
            }).append("svg:text")
                .attr("dy", ".35em")
                .attr("text-anchor", "middle")
                .attr("transform", function (d)
                {
                    return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")";
                })
                .text(function (d)
                {
                    return d.data.volumeName;
                });

            g.filter(function (d)
            {
                return d.endAngle - d.startAngle > .2;
            }).append("svg:text")
                .attr("dy", "15")
                .attr("text-anchor", "middle")
                .attr("transform", function (d)
                {
                    return "translate(" + arc.centroid(d) + ")rotate(" + angle(d) + ")";
                })
                .text(function (d)
                {
                    return d.data.usage;
                });
        });

        function angle(d)
        {
            var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
            return a > 90 ? a - 180 : a;
        }
    }
});