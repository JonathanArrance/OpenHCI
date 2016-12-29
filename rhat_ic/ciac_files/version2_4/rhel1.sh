# [INSERT 1]
#register with RHN classic
rhnreg_ks --profilename=TransCirrus_manufacturing --username=jonathan_arrance --password=transcirrus2015!
#OSP-5
rhn-channel -a -c rhel-x86_64-server-6-ost-5 -u jonathan_arrance -p transcirrus2015!
#XFS
rhn-channel -a -c rhel-x86_64-server-sfs-6 -u jonathan_arrance -p transcirrus2015!