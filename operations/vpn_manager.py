import json

from transcirrus.component.neutron.vpn import vpn_ops


def create_vpn_tunnel(auth_dict, input_dict):
    vo = vpn_ops(auth_dict)

    project_id = input_dict['project_id']
    ike_policy_name = input_dict['ike_policy_name']
    ipsec_policy_name = input_dict['ipsec_policy_name']
    service_name = input_dict['service_name']
    service_description = input_dict['service_description']
    subnet_id = input_dict['subnet_id']
    router_id = input_dict['router_id']
    peer_cidrs = input_dict['peer_cidrs']
    peer_address = input_dict['peer_address']
    tunnel_name = input_dict['tunnel_name']
    peer_id = input_dict['peer_id']

    ike_data = vo.create_vpn_ike_policy(project_id,ike_policy_name)
    ikepolicy_id = ike_data['ikepolicy']['id']

    ipsec_data = vo.create_vpn_ipsec_policy(project_id,ipsec_policy_name)
    ipsecpolicy_id = ipsec_data['ipsecpolicy']['id']

    service_data = vo.create_vpn_service(project_id, service_name, service_description, subnet_id, router_id)
    vpnservice_id = service_data['vpnservice']['id']
    vpnservice_status = service_data['vpnservice']['status']

    tunnel_data = vo.create_vpn_ipsec_site_connection(project_id, peer_cidrs, ikepolicy_id, vpnservice_id, peer_address, tunnel_name, ipsecpolicy_id, peer_id)
    tunnel_id = tunnel_data['ipsec_site_connection']['id']
    tunnel_status = tunnel_data['ipsec_site_connection']['status']

    return tunnel_data


def delete_vpn_tunnel(auth_dict, project_id, vpn_tunnel_id):

    vo = vpn_ops(auth_dict)
    vpn_tunnel_dict = vo.show_vpn_ipsec_site_connection(project_id, vpn_tunnel_id)
    results = vpn_tunnel_dict
    if vpn_tunnel_dict is not None:

        tunnel_code = vo.delete_vpn_ipsec_site_connection(project_id, vpn_tunnel_dict["ipsec_site_connection"]["id"])
        service_code = vo.delete_vpn_service(project_id, vpn_tunnel_dict["ipsec_site_connection"]["vpnservice_id"])
        ipsec_code = vo.delete_vpn_ipsec_policy(project_id, vpn_tunnel_dict["ipsec_site_connection"]["ipsecpolicy_id"])
        ike_code = vo.delete_vpn_ike_policy(project_id, vpn_tunnel_dict["ipsec_site_connection"]["ikepolicy_id"])


    #     if tunnel_code == "204" and service_code == "204" and ipsec_code == "204" and ike_code == "204":
    #         results = "Success creating VPN IPSec tunnel"
    #     else:
    #         results = "Error deleting a portion of the VPN IPSec tunnel."
    # else:
    #     results = "Error deleting VPN IPSec tunnel."

    return results


