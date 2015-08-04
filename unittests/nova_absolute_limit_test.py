from transcirrus.common.auth import authorization
from transcirrus.component.nova.absolute_limits import absolute_limits_ops

c = authorization("admin", "password")

b = c.get_auth()

ho = absolute_limits_ops(b)

project_id = "8c37340157634b29be59143240f0a5e8"
# project_id = "4633053212a84fe3aac17c1269004ecb"
# project_id = "c7644341af3942099f6363974f528112"
hl = ho.get_absolute_limit_for_tenant(project_id)
print hl
