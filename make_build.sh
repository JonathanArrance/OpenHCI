#!/bin/bash -x
DATE=$(date +"%m-%d-%Y")
git pull origin master
tar -cvf alpo_rhat_${DATE}.tar ./common ./component ./core ./database ./ha ./__init__.py ./interfaces ./operations ./SQL_files
#sudo mv ~/alpo_rhel/alpo_rhat_${DATE}.tar /var/www/builds/rhat/
#sudo rm /var/www/builds/rhat/nightly
#sudo ln -s /var/www/builds/rhat/alpo_rhat_${DATE}.tar /var/www/builds/rhat/nightly
