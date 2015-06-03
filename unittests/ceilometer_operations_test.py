from transcirrus.common.auth import authorization
import transcirrus.operations.obtain_memory_usage as memory_usage_ops

print "Get mock instance list"
instance_list = memory_usage_ops.mock_instance_list()

print "Check elements of list"
memory_usage_ops.get_mem_usage_for_instances(instance_list)