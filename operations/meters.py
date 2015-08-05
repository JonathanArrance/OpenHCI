Meters = [{"title": "Last 24hrs: Average WAC",
           "id": "wac",
           "meters": [{"label": "CPU", "meterType": "cpu_util"},
                      {"label": "Memory", "meterType": "memory.usage"},
                      {"label": "Storage", "meterType": "disk.root.size"},
                      {"label": "Disk Reads", "meterType": "disk.read.bytes.rate"},
                      {"label": "Disk Writes", "meterType": "disk.write.bytes.rate"},
                      {"label": "LAN Incoming", "meterType": "network.incoming.bytes.rate"},
                      {"label": "LAN Outgoing", "meterType": "network.outgoing.bytes.rate"}]},
          {"title": "Last 24hrs: Average Cloud Meters",
           "id": "cpu",
           "meters": [{"label": "CPU", "meterType": "compute.node.cpu.percent"},
                      {"label": "User", "meterType": "compute.node.cpu.user.percent"},
                      {"label": "Idle", "meterType": "compute.node.cpu.idle.percent"},
                      {"label": "I/O Wait", "meterType": "compute.node.cpu.iowait.percent"},
                      {"label": "Kernel", "meterType": "compute.node.cpu.kernel.percent"}]}]


def get_dashboard_meters(is_admin=None):
    if is_admin is None or is_admin == 1:
        return Meters
    else:
        for group in Meters:
            if group['id'] == "wac":
                return [group]


def get_instance_meters():
    for group in Meters:
        if group['id'] == "wac":
            return [group]
