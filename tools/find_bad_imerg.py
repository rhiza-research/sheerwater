"""Copies imerge data on your computer to the cloud."""
import glob
import gcsfs
from concurrent.futures import ThreadPoolExecutor

files = glob.glob('imerg_late/*.nc4')
files.sort()
fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')

def identify_bad_file(f):
    dat = fs.open(f).read(10)
    if 'HDF' not in str(dat):
        print(f)


ffs = fs.glob(f'gs://sheerwater-datalake/imerg_late/*.nc')

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(identify_bad_file, ffs)
