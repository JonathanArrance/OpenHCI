from transcirrus.common.auth import authorization
import transcirrus.operations.obtain_meters as meter_ops

c = authorization("admin", "password")
b = c.get_auth()
start_time = "2015-7-17T14%3A14"
end_time = "2015-7-20T14%3A14"
meter_list = {'tenant_id': None, 'resource_id': None, 'start_time': start_time, 'end_time': end_time,
              'meter_list': 'cpu_util,memory.usage,vcpus'}
result = meter_ops.get_data_for_drawing_meters(b, meter_list)
