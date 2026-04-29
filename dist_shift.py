import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    df = pd.read_pickle("histograms/kenya_sample.pkl")
    df.columns = df.columns.droplevel(0)
    # Ensure numeric index/columns
    df.index = df.index.astype(float)
    df.columns = df.columns.astype(float)

    import pdb; pdb.set_trace()

    # move along the satellite axis
    fig, ax = plt.subplots()
    for i in range(len(df.columns)):
        dist = df.iloc[:, i].values / df.iloc[:, i].values.sum()
        ax.plot(dist, color="blue", alpha=0.01)
    plt.show()


