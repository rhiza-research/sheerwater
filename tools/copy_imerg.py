"""Copies imerge data on your computer to the cloud."""
import glob
import gcsfs
from concurrent.futures import ThreadPoolExecutor

files = glob.glob('imerg_late/*.nc4')
files.sort()
fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')

def copy_file(f):
    """Copy a file to the cloud storage."""
    date = f.split('.')[4].split('-')[0]

    dest = 'gs://sheerwater-datalake/imerg_late/' + date + '.nc'

    print(f + '->' + dest)
    fs.put_file(f, dest)

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(copy_file, files)
