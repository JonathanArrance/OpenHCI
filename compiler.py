import compileall
import os


folders = ['component','common','core','database','ha','operations']

for folder in folders:
    print folder
    compileall.compile_dir("/usr/local/lib/python2.7/transcirrus/" + folder,force=1)

for root, dirs, files in os.walk("/usr/local/lib/python2.7/transcirrus"):
    if(root == 'interfaces'):
        continue
    for raw in files:
        f = raw.split('.')
        if(f[0] == 'config'):
            continue
        else:
            os.system("sudo rm %s/%s.py"%(root,f[0]))
        #os.remove(glob.glob("%s/*.py"%(str(root))))

compileall.compile_dir("/opt/" + folder,force=1)

for root, dirs, files in os.walk("/opt"):
    for raw in files:
        f = raw.split('.')
        if(f[0] == 'config'):
            continue
        else:
            os.system("sudo rm %s/%s.py"%(root,f[0]))