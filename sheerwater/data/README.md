# Data access folder

## Overview

This folder contains code to access and prepare various datasets used by the Sheerwater project. Each dataset is exposed via a specific function. For most datasets, if you have proper permissions to our datalake, you can use these functions directly without additional setup.

### How to Access Data

- **For most external users:**  
  - Ensure you have read access to our datalake.
  - Import the relevant function(s) from this package.
  - Call the function to retrieve the data as needed.

- **For maintainers/contributors:**  
 - CHIRP(S): Fully documented and runnable by the code. Currently some of the datasources only go back to 2000, and CHIRPS3-SAT only back to 1998.
 - IMERG: We manually download the IMERG netcdfs by going to this website https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDL_07/summary?keywords=%22IMERG%20late%22 logging in, downloading the filelist, then following the curl fetch instructions here https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Access%20GES%20DISC%20Data%20Using%20wget%20and%20curl, then finally uploading them to our datalake with tools/copy_imerg.py. Make sure to final in gs://sheerwater-datalake/imerg and late in gs://sheerwater-datalake/imerg_late
 - TAHMO: TODO
 - GHCN: Should be fully documented/runnable by the code, but it's slow because the GHCN data is large and must fit entierly within a single machine's memeory to grid. 
