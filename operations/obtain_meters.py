import re

from transcirrus.component.ceilometer.ceilometer_meters import meter_ops
from transcirrus.component.nova.absolute_limits import absolute_limits_ops
from transcirrus.component.nova.hypervisor import hypervisor_ops


def get_data_for_drawing_meters(auth_dict, input_dict):
    if auth_dict['is_admin'] == 1:
        # ADMIN ONLY
        hypervisor_results = get_hypervisor_info(auth_dict)
        quota_results = get_absolute_limit_for_project(auth_dict)
        ceilometer_results = get_ceilometer_usage_for_meters(input_dict, auth_dict)

        results = normalize_data(input_dict, quota_results, ceilometer_results, hypervisor_results)

    else:
        # GENERAL USERS
        quota_results = get_absolute_limit_for_project(auth_dict)
        ceilometer_results = get_ceilometer_usage_for_meters(input_dict, auth_dict)

        results = normalize_data(input_dict, quota_results, ceilometer_results, None)

    return results


def normalize_data(input_dict, quota, ceilometer, hypervisor=None):
    results = []

    meter_list = input_dict['meter_list']
    meters = meter_list.split(",")
    for meter in meters:
        for ceilometerData in ceilometer:
            if ceilometerData['meter_type'] == meter:
                if meter == "memory.usage":
                    meter_dict = ({'meterName': meter,
                                   'htmlID': re.sub(r"['_,!\-\"\\\/}{?\.]", '', meter).strip().replace(" ", ""),
                                   'minValue': 0,
                                   'maxValue': quota['limits']['absolute']['maxTotalRAMSize'],
                                   'unitMeasurement': ceilometerData['unit'],
                                   'utilization': ceilometerData['avg'],
                                   'statisticsType': 'average',
                                   'chartType': 'radial',
                                   'quotaLimit': quota['limits']['absolute']['maxTotalRAMSize']})
                elif meter == "cpu_util" or ".cpu." in meter:
                    meter_dict = ({'meterName': meter,
                                   'htmlID': re.sub(r"['_,!\-\"\\\/}{?\.]", '', meter).strip().replace(" ", ""),
                                   'minValue': 0,
                                   'maxValue': 100,
                                   'unitMeasurement': ceilometerData['unit'],
                                   'utilization': ceilometerData['avg'],
                                   'statisticsType': 'average',
                                   'chartType': 'radial',
                                   'quotaLimit': None})
                elif meter == "vcpus":
                    meter_dict = ({'meterName': meter,
                                   'htmlID': re.sub(r"['_,!\-\"\\\/}{?\.]", '', meter).strip().replace(" ", ""),
                                   'minValue': 0,
                                   'maxValue': quota['limits']['absolute']['maxTotalCores'],
                                   'unitMeasurement': ceilometerData['unit'],
                                   'utilization': ceilometerData['avg'],
                                   'statisticsType': 'average',
                                   'chartType': 'counter',
                                   'quotaLimit': quota['limits']['absolute']['maxTotalCores']})
                elif meter == "disk.root.size":
                    meter_dict = ({'meterName': meter,
                                   'htmlID': re.sub(r"['_,!\-\"\\\/}{?\.]", '', meter).strip().replace(" ", ""),
                                   'minValue': 0,
                                   'maxValue': ceilometerData['max'] if hypervisor is None else
                                   hypervisor['hypervisor_statistics']['local_gb'],
                                   'unitMeasurement': ceilometerData['unit'],
                                   'utilization': ceilometerData['avg'] if hypervisor is None else
                                   hypervisor['hypervisor_statistics']['local_gb_used'],
                                   'statisticsType': 'average',
                                   'chartType': 'radial',
                                   'quotaLimit': None})
                else:
                    meter_dict = ({'meterName': meter,
                                   'htmlID': re.sub(r"['_,!\-\"\\\/}{?\.]", '', meter).strip().replace(" ", ""),
                                   'minValue': 0,
                                   'maxValue': None,
                                   'unitMeasurement': ceilometerData['unit'],
                                   'utilization': ceilometerData['avg'],
                                   'statisticsType': 'average',
                                   'chartType': 'counter',
                                   'quotaLimit': None})
                results.append(meter_dict)

    return results


def get_hypervisor_info(auth_dict):
    # This function can only be called by an admin

    hypervisor = hypervisor_ops(auth_dict)
    project_id = auth_dict['project_id']
    results = hypervisor.get_hypervisor_stats(project_id)

    return results


def get_absolute_limit_for_project(auth_dict):
    abs_limit = absolute_limits_ops(auth_dict)
    project_id = auth_dict['project_id']
    results = abs_limit.get_absolute_limit_for_tenant(project_id)

    return results


def get_ceilometer_usage_for_meters(input_dict, auth_dict):
    mo = meter_ops(auth_dict)
    project_id = auth_dict['project_id']
    tenant_identifier = input_dict['tenant_id']
    resource_identifier = input_dict['resource_id']
    start_time = input_dict['start_time']
    end_time = input_dict['end_time']
    meter_list = input_dict['meter_list']
    meters = meter_list.split(",")
    results = mo.show_stats_for_meter_list(project_id, start_time, end_time, meters, tenant_identifier,
                                           resource_identifier)

    return results
