import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def level_counts(df, levels):
    result = pd.DataFrame(
        0.0,
        index=levels.keys(),
        columns=levels.keys()
    )

    idx = df.index.values
    cols = df.columns.values

    for li_name, (i0, i1) in levels.items():
        i_mask = (idx >= i0) & (idx < i1)

        for lj_name, (j0, j1) in levels.items():
            j_mask = (cols >= j0) & (cols < j1)

            sub = df.loc[i_mask, j_mask].to_numpy().sum()
            result.loc[li_name, lj_name] = sub

    return result


if __name__ == "__main__":
    df = pd.read_pickle("histograms/kenya_sample.pkl")
    df.columns = df.columns.droplevel(0)
    # Ensure numeric index/columns
    df.index = df.index.astype(float)
    df.columns = df.columns.astype(float)

    levels = {"lo": [0, 2], "med": [5, 10], "hi": [15, 20]}
    cts = level_counts(df, levels)
    import pdb; pdb.set_trace()





    


