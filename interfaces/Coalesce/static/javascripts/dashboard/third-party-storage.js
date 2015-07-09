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

    // Configure
    $(document).on('click', '.configure', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_storage/get_configure/' + provider + '/';
        showModal(call);
    });

    $(document).on('click', '#confirm-configure', function (event) {
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
});

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