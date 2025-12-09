"""Copies imerge data on your computer to the cloud."""
import gcsfs
from concurrent.futures import ThreadPoolExecutor

fs = gcsfs.GCSFileSystem(project='sheerwater', token='google_default')

def identify_bad_file(f):
    """Identifies a bad IMERG file."""
    dat = fs.open(f).read(10)
    if 'HDF' not in str(dat):
        print(f)


ffs = fs.glob('gs://sheerwater-datalake/imerg_late/202*.nc')

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(identify_bad_file, ffs)
