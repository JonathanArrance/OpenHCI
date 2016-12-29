# [INSERT 4]
psql -U postgres -d transcirrus -c "INSERT INTO factory_defaults VALUES ('physical_node','1','"${HOSTNAME}"');"