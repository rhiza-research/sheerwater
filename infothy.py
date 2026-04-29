import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# (2) Convert to conditional distributions P(estimate | truth)
def to_conditional(df, eps=1e-12):
    P = df.values.astype(float) + eps
    P /= P.sum(axis=0, keepdims=True)  # normalize columns
    return pd.DataFrame(P, index=df.index, columns=df.columns)


# (3a) KL divergence matrix
def kl_divergence_df(P_df, eps=1e-12, symmetric=False):
    P = P_df.values + eps
    n = P.shape[1]

    KL = np.zeros((n, n))

    for i in range(n):
        p = P[:, i]
        for j in range(n):
            q = P[:, j]
            KL[i, j] = np.sum(p * np.log(p / q))

    if symmetric:
        KL = 0.5 * (KL + KL.T)

    return pd.DataFrame(KL, index=P_df.columns, columns=P_df.columns)


# (3b) Hellinger distance matrix
def hellinger_df(P_df, eps=1e-12):
    P = P_df.values + eps
    n = P.shape[1]

    H = np.zeros((n, n))

    for i in range(n):
        p = np.sqrt(P[:, i])
        for j in range(n):
            q = np.sqrt(P[:, j])
            H[i, j] = np.sqrt(0.5 * np.sum((p - q) ** 2))

    return pd.DataFrame(H, index=P_df.columns, columns=P_df.columns)

def aggregate_distance(df, start=0):
    distances = np.nan * np.ones(len(df.columns))
    for i in range(start, len(df.columns)):
        P = df.iloc[:, start:i+1].sum(axis=1)
        P = P / P.sum()
        Q = df.iloc[:, i]
        Q = Q / Q.sum()
        distances[i] = np.sqrt(0.5 * np.sum((np.sqrt(P) - np.sqrt(Q)) ** 2))
    return distances

import numpy as np

def make_dist(df):
    eps = 1e-12
    df = df + eps
    return df / df.sum(axis=0)


def hellinger(P, Q):
    return np.sqrt(0.5 * np.sum((np.sqrt(P) - np.sqrt(Q)) ** 2))

def get_bins1(df, max_bin_len=10, bin_dist=0.3):
    bin_starts = []
    bin_ends = []

    curr_start = 0
    P = make_dist(df.iloc[:, 0])
    waiting = False

    for i in range(1, len(df.columns)):
        Q = make_dist(df.iloc[:, i])
        dist = hellinger(P, Q)

        if not waiting:
            if dist > bin_dist:
                # close bin, start new one
                bin_starts.append(curr_start)
                bin_ends.append(i - 1)

                curr_start = i
                P = Q

            elif (i - curr_start + 1) > max_bin_len:
                # close bin, but DO NOT start new one
                bin_starts.append(curr_start)
                bin_ends.append(i - 1)

                waiting = True  # enter waiting mode

            else:
                # keep growing bin
                P = make_dist(df.iloc[:, curr_start:i+1].sum(axis=1))

        else:
            # --- waiting mode ---
            if dist > bin_dist:
                # start new bin here
                curr_start = i
                P = Q
                waiting = False

            # else: keep waiting (do nothing)

    # close final bin if active
    if not waiting:
        bin_starts.append(curr_start)
        bin_ends.append(len(df.columns) - 1)

    return bin_starts, bin_ends

def make_dist_col(col):
    eps = 1e-12
    col = col.values.astype(float) + eps
    return col / col.sum()


def central_interval(p, mass_keep):
    """
    Return index range [lo, hi] covering mass_keep around mean.
    """
    x = np.arange(len(p))
    mean = np.sum(x * p)

    # sort indices by distance to mean
    order = np.argsort(np.abs(x - mean))

    cum = 0.0
    selected = []

    for idx in order:
        selected.append(idx)
        cum += p[idx]
        if cum >= mass_keep:
            break

    lo = min(selected)
    hi = max(selected)
    return lo, hi


def get_bins3(df, max_bin_len=10, poverlap=0.1):
    bin_starts = []
    bin_ends = []
    bin_los = []
    bin_his = []

    curr_start = 0
    waiting = False

    # initialize first bin distribution
    P = make_dist_col(df.iloc[:, 0])
    lo, hi = central_interval(P, 0.5)

    for i in range(1, len(df.columns)):
        Q = make_dist_col(df.iloc[:, i])

        overlap = Q[lo:hi+1].sum()

        if not waiting:
            if overlap <= poverlap:
                import pdb; pdb.set_trace()
                # --- start new bin ---
                bin_starts.append(curr_start)
                bin_ends.append(i - 1)
                bin_los.append(lo)
                bin_his.append(hi)

                curr_start = i
                P = Q
                lo, hi = central_interval(P, 1 - poverlap)

            elif (i - curr_start + 1) > max_bin_len:
                # --- close but wait ---
                bin_starts.append(curr_start)
                bin_ends.append(i - 1)
                bin_los.append(lo)
                bin_his.append(hi)

                waiting = True

            else:
                # --- accumulate ---
                P = make_dist_col(df.iloc[:, curr_start:i+1].sum(axis=1))
                lo, hi = central_interval(P, 1 - poverlap)

        else:
            # --- waiting mode ---
            if overlap <= poverlap:
                import pdb; pdb.set_trace()
                curr_start = i
                P = Q
                lo, hi = central_interval(P, 1 - poverlap)
                waiting = False

            # else: keep waiting

    # close final bin
    if not waiting:
        bin_starts.append(curr_start)
        bin_ends.append(len(df.columns) - 1)
        bin_los.append(lo)
        bin_his.append(hi)

    return bin_starts, bin_ends, bin_los, bin_his

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def plot_bins_rectangles(df, bin_starts, bin_ends, bin_los, bin_his):
    fig, ax = plt.subplots(figsize=(8, 6))

    im = ax.imshow(df.values, aspect='auto', origin='lower')

    for s, e, lo, hi in zip(bin_starts, bin_ends, bin_los, bin_his):
        rect = Rectangle(
            (s - 0.5, lo - 0.5),          # bottom-left corner
            (e - s + 1),                 # width (inclusive)
            (hi - lo + 1),               # height (inclusive)
            edgecolor='red',
            facecolor='none',
            linewidth=2
        )
        ax.add_patch(rect)

    ax.set_xlabel("truth (column index)")
    ax.set_ylabel("estimate (row index)")

    fig.colorbar(im, ax=ax)
    plt.show()


if __name__ == "__main__":
    df = pd.read_pickle("histograms/kenya_sample.pkl")
    df.columns = df.columns.droplevel(0)
    # Ensure numeric index/columns
    df.index = df.index.astype(float)
    df.columns = df.columns.astype(float)
    # clip to ground truth where we have more than 100 samples
    df = df.loc[df.sum(axis=0) > 400]

    bin_starts, bin_ends = get_bins1(df, max_bin_len=10, bin_dist=0.7)
    bin_starts3, bin_ends3, bin_los3, bin_his3 = get_bins3(df, max_bin_len=10, poverlap=0.4)
    plot_bins_rectangles(df, bin_starts3, bin_ends3, bin_los3, bin_his3)
    import pdb; pdb.set_trace()

    fig, ax = plt.subplots()
    starts = np.arange(0, 20)
    for start in starts:
        distances = aggregate_distance(df, start=start)
        ax.plot(distances, label=f"start={start}")

    ax.legend()
    plt.show()
    import pdb; pdb.set_trace()

    # conditional distributions
    P_df = to_conditional(df)

    # divergences
    kl_df = kl_divergence_df(P_df, symmetric=False)
    kl_sym_df = kl_divergence_df(P_df, symmetric=True)
    hell_df = hellinger_df(P_df)

    # lets plot these
    fig, ax = plt.subplots()
    for i in range(100):
        x = hell_df.iloc[i]
        x[x == 0] = np.nan
        plt.plot(x, color="blue", alpha=0.1)
    plt.show()

    import pdb; pdb.set_trace()