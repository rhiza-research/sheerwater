# Data access folder

To access this data externally you should just be able to access the exposed function for each if you have read access to our datalake.

## Internal notes for fetching data

 - CHIRP(S): Fully documented/runnable by the code. Currently Some of the datasources only go back to 2000, and CHIRPS3-SAT only back to 1998.
 - IMERG: I manually download the IMERG netcdfs by going to this website https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDL_07/summary?keywords=%22IMERG%20late%22 logging in, downloading the filelist, then
            following the curl fetch instructions here https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Access%20GES%20DISC%20Data%20Using%20wget%20and%20curl then uploading
            them to our datalake with tools/copy_imerg.py. Make sure you put final in gs://sheerwater-datalake/imerg and late in gs://sheerwater-datalake/imerg_late
 - TAHMO: TODO
 - GHCN: Should be fully documented/runnalbe by the code, but it's slow
