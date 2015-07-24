function generateDonut(id, label, data) {
    id = '#' + id;
    return c3.generate({
        bindto: id,
        data: {
            columns: data,
            type: 'donut',
            onclick: function (d, i) {
            },
            onmouseover: function (d, i) {
            },
            onmouseout: function (d, i) {
            }
        },
        donut: {
            title: label,
            label: {
                format: function (value, ratio, id) {
                    return value;
                },
                show: true
            }
        },
        color: {
            pattern: ['#5bc0de', '#5cb85c', '#f0ad4e', '#df691a', '#d9534f']
        },
        legend: {
            position: "bottom",
            show: false
        },
        padding: {
            right: 100,
            left: 100
        },
        size: {
            height: 280,
            width: 280
        },
        tooltip: {
            position: function (data, width, height, element) {
                var x = currentMousePosition["x"] - $(id).offset().left + 10;
                var y = currentMousePosition["y"] - $(id).offset().top;
                return {top: y, left: x}
            },
            format: {
                value: function (value, ratio, id) {
                    return value;
                }
            }
        }
    });
}

function generateGauge(id, min, max, label, units, data) {
    id = '#' + id;
    return c3.generate({
        bindto: id,
        data: {
            columns: [
                ['data', parseInt(data)]
            ],
            type: 'gauge',
            onclick: function (d, i) {
            },
            onmouseover: function (d, i) {
            },
            onmouseout: function (d, i) {
            }
        },
        gauge: {
            label: {
                format: function (value, ratio) {
                    return value;
                },
                show: true
            },
            min: min,
            max: max,
            width: 60
        },
        color: {
            pattern: ['#5bc0de', '#5cb85c', '#f0ad4e', '#d9534f'],
            threshold: {
                unit: 'value',
                max: max,
                values: [(max * .30), (max * .60), (max * .90), max]
            }
        },
        size: {
            height: 150,
            width: 280
        },
        title: {
            text: label + " " + units,
            position: "center",
            show: true
        },
        tooltip: {
            show: false
        }
    })
}

function generateBar(id, units, data, pattern) {
    id = '#' + id;
    return c3.generate({
        bindto: id,
        data: {
            columns: data,
            type: 'bar',
            onclick: function (d, i) {
            },
            onmouseover: function (d, i) {
            },
            onmouseout: function (d, i) {
            }
        },
        bar: {
            width: {
                ratio: 1
            }
        },
        axis: {
            x: {
                label: {
                    text: units,
                    position: 'inner-right'
                },
                show: true,
                tick: {
                    format: function () {
                        return ""
                    }
                }
            }
        },
        color: {
            pattern: pattern === undefined ? ['#f0ad4e', '#5cb85c', '#d9534f', '#5bc0de'] : undefined
        },
        size: {
            width: 280,
            height: 260
        },
        tooltip: {
            position: function (data, width, height, element) {
                var x = currentMousePosition["x"] - $(id).offset().left + 10;
                var y = currentMousePosition["y"] - $(id).offset().top;
                return {top: y, left: x}
            },
            format: {
                value: function (value, ratio, id) {
                    return value;
                }
            }
        }
    });
}

