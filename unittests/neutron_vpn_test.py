#!/usr/bin/python
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.vpn import vpn_ops

c = authorization("admin", "password")
b = c.get_auth()
vo = vpn_ops(b)
print vo

print "Listing vpn ike policies"
project_id = "29bffa02efa9451f9968483f020f2278"
l1a = vo.list_vpn_ike_policy(project_id)
print l1a

# print "Create vpn ike policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_name = "ikepolicy12"
# l1b = vo.create_vpn_ike_policy(project_id,policy_name)
# print l1b

# print "Show vpn ike policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_id = "e1fb3870-58ba-4015-8674-cec98dcfc234"
# l1c = vo.show_vpn_ike_policy(project_id,policy_id)
# print l1c

# print "Delete vpn ike policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_id = "e1fb3870-58ba-4015-8674-cec98dcfc234"
# l1d = vo.delete_vpn_ike_policy(project_id,policy_id)
# print l1d

print "Listing vpn ipsec policy"
project_id = "29bffa02efa9451f9968483f020f2278"
l2a = vo.list_vpn_ipsec_policy(project_id)
print l2a

# print "Create vpn ipsec policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_name = "ipsecpolicy50"
# l2b = vo.create_vpn_ipsec_policy(project_id,policy_name)
# print l2b

# print "Show vpn ipsec policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_id = "b0721a00-578b-46a5-8110-c57934fed17b"
# l3c = vo.show_vpn_ipsec_policy(project_id,policy_id)
# print l3c

# print "Delete vpn ipsec policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# policy_id = "b0721a00-578b-46a5-8110-c57934fed17b"
# l4d = vo.delete_vpn_ipsec_policy(project_id,policy_id)
# print l4d


print "Listing vpn service list"
project_id = "29bffa02efa9451f9968483f020f2278"
l3a = vo.list_vpn_service(project_id)
print l3a

# print "Create vpn service policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# service_name = "myvpn01"
# service_description = "Description"
# subnet_id = "6e1a146d-ba4d-4463-9885-2313124b01fb"
# router_id = "02f71c83-fdc2-45fa-b49f-df7cb4041385"
# l3b = vo.create_vpn_service(project_id, service_name, service_description, subnet_id, router_id)
# print l3b

# print "Show vpn service policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# service_id = "64ba1d3a-136b-4707-8eea-269657ea5417"
# l3c = vo.show_vpn_service(project_id,service_id)
# print l3c

# print "Delete vpn service policy"
# project_id = "29bffa02efa9451f9968483f020f2278"
# service_id = "64ba1d3a-136b-4707-8eea-269657ea5417"
# l3d = vo.delete_vpn_service(project_id,service_id)
# print l3d

print "Listing vpn ipsec site connection"
project_id = "29bffa02efa9451f9968483f020f2278"
l4a = vo.list_vpn_ipsec_site_connection(project_id)
print l4a

# print "Create vpn ipsec site connection"
# project_id = "29bffa02efa9451f9968483f020f2278"
# peer_cidrs = "10.0.1.0/24"
# ikepolicy_id = "0dc840b6-d88c-4afd-9392-c00c6ad0585d"
# vpnservice_id = "190422d0-6a8a-4550-a5b9-6932c2651756"
# peer_address = "192.168.2.72"
# tunnel_name = "vpnconnection12"
# ipsecpolicy_id = "f9e69502-d5a1-42d2-9ab8-d0c823defff4"
# peer_id = "192.168.2.72"
# l4b = vo.create_vpn_ipsec_site_connection(project_id, peer_cidrs, ikepolicy_id, vpnservice_id, peer_address, tunnel_name, ipsecpolicy_id, peer_id)
# print l4b

# print "Show vpn ipsec site connection"
# project_id = "29bffa02efa9451f9968483f020f2278"
# tunnel_id = "b456e33d-6ec9-4576-8a23-ec109a64b7d1"
# l4c = vo.show_vpn_ipsec_site_connection(project_id,tunnel_id)
# print l4c

# print "Delete vpn ipsec site connection"
# project_id = "29bffa02efa9451f9968483f020f2278"
# tunnel_id = "b456e33d-6ec9-4576-8a23-ec109a64b7d1"
# l4d = vo.delete_vpn_ipsec_site_connection(project_id,tunnel_id)
# print l4d