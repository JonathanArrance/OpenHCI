import compileall
import os
import glob


folders = ['component','common','core','database','ha','interfaces','operations']

for folder in folders:
    print folder
    compileall.compile_dir(folder,force=1)

for root, dirs, files in os.walk("."):
    for raw in files:
        f = raw.split('.')
        if(f[0] == 'config'):
            continue
        else:
            os.system("sudo rm %s/%s.py"%(root,f[0]))
        #os.remove(glob.glob("%s/*.py"%(str(root))))