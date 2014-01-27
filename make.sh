mkdir -p /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding common to Transcirrus dir'
cp -Rf common /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding component to Transcirrus dir'
cp -Rf component /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding core to Transcirrus dir'
cp -Rf core /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding database to Transcirrus dir'
cp -Rf database /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding operations to Transcirrus dir'
cp -Rf operations /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding Interfaces to Transcirrus dir'
cp -Rf interfaces /usr/local/lib/python2.7/dist-packages/transcirrus/
echo 'Adding ha to Transcirrus dir'
cp -Rf ha /usr/local/lib/python2.7/dist-packages/transcirrus/
cp -f __init__.py /usr/local/lib/python2.7/dist-packages/transcirrus/

#check to see if the log file exists
if [ -e /var/log/caclogs/system.log ]
then
echo "CAClog exists"
else
mkdir -p /var/log/caclogs
touch /var/log/caclogs/system.log
chmod -R 776 /var/log/caclogs
chown -R transuser:transystem /var/log/caclogs
fi

#add the django site to its proper place in the file system
echo 'Adding Coalesce to the opt directory.'
#cp -Rf ./interfaces/Coalesce /opt
#chown -R transuser:transystem /opt/Coalesce

#add the shell to its proper place

#restart the apache2 service
service apache2 restart
 
