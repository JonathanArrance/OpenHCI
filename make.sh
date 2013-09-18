mkdir -p /usr/lib/python2.7/dist-packages/transcirrus/

echo 'Adding common to Transcirrus dir'
cp -Rf ./common /usr/lib/python2.7/dist-packages/transcirrus/
echo 'Adding component to Transcirrus dir'
cp -Rf ./component /usr/lib/python2.7/dist-packages/transcirrus/
echo 'Adding core to Transcirrus dir'
cp -Rf ./core /usr/lib/python2.7/dist-packages/transcirrus/
echo 'Adding database to Transcirrus dir'
cp -Rf ./database /usr/lib/python2.7/dist-packages/transcirrus/
echo 'Adding tasks to Transcirrus dir'
cp -Rf ./tasks /usr/lib/python2.7/dist-packages/transcirrus/
echo 'Adding ha to Transcirrus dir'
cp -Rf ./ha /usr/lib/python2.7/dist-packages/transcirrus/


#add the django site to its proper place in the file system

#add the shell to its proper place

#restart the apache2 service
service apache2 restart
 
