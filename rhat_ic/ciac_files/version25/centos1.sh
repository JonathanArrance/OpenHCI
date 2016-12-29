# [INSERT 1]
#add postgres to the yum repos files
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.old
wget -P /etc/yum.repos.d/ http://192.168.10.10/rhat_ic/ciac_files/CentOS-Base.repo