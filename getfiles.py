from os import listdir
from os.path import isfile, join

mypath = "/home/akshaya/technical/tinker-box/database/211013/pcd-files-downsampled"
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
print onlyfiles[0]