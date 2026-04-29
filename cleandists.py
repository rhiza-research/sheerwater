import pandas as pd
import os
import glob

root = "histograms"

# find all pkl files in the root directory
pkl_files = glob.glob(os.path.join(root, "*.pkl"))

# load each pkl file
for pkl_file in pkl_files:
    df = pd.read_pickle(pkl_file)
    #df.columns = df.columns.droplevel(0)
    #df.index = df.index.astype(float)
    #df.columns = df.columns.astype(float)
    # round index and columns to 1 decimal place
    df.index = df.index.round(1)
    df.columns = df.columns.round(1)
    # save to pkl
    df.to_pickle(pkl_file)