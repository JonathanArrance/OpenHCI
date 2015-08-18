from transcirrus.common.auth import authorization
import transcirrus.operations.flavor_resize_list as flavor_resize_ops

c = authorization("admin", "password")
b = c.get_auth()

instance_id = "b4892ad1-f8d0-48e0-a3f2-8ad6e182868e"
project_id = "19d52f8bb4ea4647a6f394058ed7a984"
result = flavor_resize_ops.get_list_of_valid_resizeable_flavors(b, project_id, instance_id)
print result