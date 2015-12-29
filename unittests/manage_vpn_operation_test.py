from transcirrus.common.auth import authorization
import transcirrus.operations.vpn_manager as vpn_operation

c = authorization("admin", "password")
auth_dict = c.get_auth()

input_dict = {
    "project_id": "f350af0a3d4d4bc49fe980fa1f99c2f3",
    "ike_policy_name": "ikepolicy01",
    "ipsec_policy_name": "ipsecpolicy01",
    "service_name": "myvpn01",
    "service_description": "some description",
    "subnet_id": "0c0ed39f-8672-4777-8f94-50b1bb8398e0",
    "router_id": "3f31dfe0-e8a8-48c1-a8cf-52efba13ac53",
    "peer_cidrs": "10.0.0.1/24",
    "peer_address": "192.168.10.71",
    "peer_id": "192.168.10.71",
    "tunnel_name": "vpnconnection01"
}

# result1 = vpn_operation.create_vpn_tunnel(auth_dict, input_dict)
# print result1
print "------------------------------------------------"
result2 = vpn_operation.delete_vpn_tunnel(auth_dict, "29bffa02efa9451f9968483f020f2278", "287e6bf6-fe64-4db9-b5fe-140addc1f909")
print result2


project_id,ike_policy_name,ipsec_policy_name,service_name,service_description,subnet_id,router_id,peer_cidrs,peer_address,peer_id,tunnel_name