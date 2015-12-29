from transcirrus.common.auth import authorization
import transcirrus.operations.vpn_manager as vpn_operation

c = authorization("admin", "password")
auth_dict = c.get_auth()

input_dict = {
    "project_id": "29bffa02efa9451f9968483f020f2278",
    "ike_policy_name": "ikepolicy12",
    "ipsec_policy_name": "ipsecpolicy50",
    "service_name": "myvpn05",
    "service_description": "some description",
    "subnet_id": "6e1a146d-ba4d-4463-9885-2313124b01fb",
    "router_id": "02f71c83-fdc2-45fa-b49f-df7cb4041385",
    "peer_cidrs": "10.0.1.0/24",
    "peer_address": "192.168.2.72",
    "peer_id": "192.168.2.72",
    "tunnel_name": "vpnconnection50"
}

result1 = vpn_operation.create_vpn_tunnel(auth_dict, input_dict)
print result1
print "------------------------------------------------"
result2 = vpn_operation.delete_vpn_tunnel(auth_dict, "29bffa02efa9451f9968483f020f2278", "9c84c052-a50c-46a5-b30e-05247ef58bbc")
print result2
