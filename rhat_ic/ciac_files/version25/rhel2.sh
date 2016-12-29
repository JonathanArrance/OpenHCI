# [INSERT 3]
#update ceilometer policy for rhel
rm -f /etc/ceilometer/policy.json
touch /etc/ceilometer/policy.json
(
cat <<'EOP'
{
    "context_is_admin": [["role:admin"]],
    "segregation": [["rule:context_is_admin"]]
}
EOP
) >> /etc/ceilometer/policy.json
chmod 770 /etc/ceilometer/policy.json
chmod +x /etc/ceilometer/policy.json
chown ceilometer:ceilometer /etc/ceilometer/policy.json