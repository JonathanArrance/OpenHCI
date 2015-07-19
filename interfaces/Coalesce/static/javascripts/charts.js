function generateDonut(id, label) {
    id = '#' + id;
    return c3.generate({
        bindto: id,
        data: {
            columns: [
                ['', 1]
            ],
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
            position: "right",
            show: true
        },
        padding: {
            right: 100,
            left: 100
        },
        size: {
            height: 400,
            width: 615
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

function generateGauge(id, min, max, label) {
    id = '#' + id;
    return c3.generate({
        bindto: id,
        data: {
            columns: [
                ['data', 0]
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
                show: true // to turn off the min/max labels.
            },
            min: min, // 0 is default, //can handle negative min e.g. vacuum / voltage / current flow / rate of change
            max: max, // 100 is default
            width: 75 // for adjusting arc thickness
        },
        color: {
            pattern: ['#5bc0de', '#5cb85c', '#f0ad4e', '#d9534f'], // the three color levels for the percentage values.
            threshold: {
                unit: 'value', // percentage is default
                max: max, // 100 is default
                values: [(max * .30), (max * .60), (max * .90), max]
            }
        },
        size: {
            height: 140,
            width: 240
        },
        padding: {
            top: 0
        },
        title: {
            text: label,
            position: "center"
        },
        tooltip: {
            show: false
        }
    })
}

