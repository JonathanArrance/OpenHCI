DashboardMeters = [
    {
        "title": "Last 24hrs: Average WAC",
        "id": "wac",
        "meters": [
            {"id": "cpu-util", "label": "CPU %", "meterType": "cpu_util", "calcType": "avg", "min": 0, "max": 100,
             "minorTicks": 5, 'units': '%'},
            {"id": "memory-usage", "label": "Memory (mb)", "meterType": "memory.usage", "calcType": "avg", "min": 0,
             "max": 128000, "minorTicks": 8, 'units': '(mb)'},
            {"id": "disk-root-size", "label": "Storage (gb)", "meterType": "disk.root.size", "calcType": "avg",
             "min": 0,
             "max": 1000, "minorTicks": 8, 'units': '(gb)'},
            {"id": "disk-read-bytes-rate", "label": "Disk Reads B/s", "meterType": "disk.read.bytes.rate",
             "calcType": "avg",
             "min": 0, "max": 100000, "minorTicks": 8, 'units': 'B/s'},
            {"id": "disk-write-bytes-rate", "label": "Disk Writes B/s", "meterType": "disk.write.bytes.rate",
             "calcType": "avg",
             "min": 0, "max": 100000, "minorTicks": 8, 'units': '%'}]
    },
    {
        "title": "Last 24hrs: Average Cloud Meters",
        "id": "cpu",
        "meters": [
            {"id": "compute-node-cpu-percent", "label": "% CPU", "meterType": "compute.node.cpu.percent",
             "calcType": "avg", "min": 0, "max": 100, "minorTicks": 5, 'units': '%'},
            {"id": "compute-node-cpu-user-percent", "label": "% User",
             "meterType": "compute.node.cpu.user.percent", "calcType": "avg", "min": 0, "max": 100,
             "minorTicks": 5, 'units': '%'}, {"id": "compute-node-cpu-idle-percent", "label": "% Idle",
                                              "meterType": "compute.node.cpu.idle.percent",
                                              "calcType": "avg", "min": 0, "max": 100, "minorTicks": 5,
                                              'units': '%'},
            {"id": "compute-node-cpu-iowait-percent", "label": "% I/O Wait",
             "meterType": "compute.node.cpu.iowait.percent", "calcType": "avg", "min": 0, "max": 100,
             "minorTicks": 5, 'units': '%'},
            {"id": "compute-node-cpu-kernal-percent", "label": "% Kernal",
             "meterType": "compute.node.cpu.kernal.percent", "calcType": "avg", "min": 0, "max": 100,
             "minorTicks": 5, 'units': '%'}]
    }]
Wac = DashboardMeters[0]

def get_dashboard_meters(is_admin=None):
    if (is_admin == None or is_admin == 1):
        return DashboardMeters
    else:
        return Wac

        # UNUSED WAC GAUGES
        # {"id": "network-incoming-bytes-rate", "label": "LAN Incoming B/s", "meterType": "network.incoming.bytes.rate", "calcType": "avg", "min": 0, "max": 10000, "minorTicks": 8, 'units': 'B/s'},
        # {"id": "network-outgoing-bytes-rate", "label": "LAN Outgoing B/s", "meterType": "network.outgoing.bytes.rate", "calcType": "avg", "min": 0, "max": 10000, "minorTicks": 8, 'units': 'B/s'},
        # {"id": "wan-incoming-bytes-rate", "label": "WAN Incoming B/s", "meterType": "wan.incoming.bytes.rate", "calcType": "avg", "min": 0, "max": 10000, "minorTicks": 8, 'units': 'B/s'},
        # {"id": "wan-outgoing-bytes-rate", "label": "WAN Outgoing B/s", "meterType": "wan.outgoing.bytes.rate", "calcType": "avg", "min": 0, "max": 10000, "minorTicks": 8, 'units': 'B/s'}
