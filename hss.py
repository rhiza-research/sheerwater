import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

def category_grid(xbuckets=None, ncategories=None, width=5, gap=0.5):

    if xbuckets is None:
        xbuckets = [(i*(width+gap), i*(width+gap)+width) for i in range(ncategories)]

    step = width + gap

    # extend ybuckets on both sides
    margin = 2
    extra_low  = [(xbuckets[0][0] - step*(i+1), xbuckets[0][1] - step*(i+1)) for i in range(margin)][::-1]
    extra_high = [(xbuckets[-1][0] + step*(i+1), xbuckets[-1][1] + step*(i+1)) for i in range(margin)]

    ybase = extra_low + xbuckets + extra_high

    ybuckets = [list(ybase) for _ in xbuckets]

    return xbuckets, ybuckets

def recenter_categories(df, xbuckets, ybuckets, shift=True):
    new_ybuckets = []
    ymles = []

    for i, (xs, xe) in enumerate(xbuckets):
        sub = df.loc[:, (df.columns >= xs) & (df.columns < xe)]
        y_counts = sub.sum(axis=1).values

        if y_counts.sum() == 0:
            ymle = df.index[len(df.index)//2]
        else:
            ymle = df.index[np.argmax(y_counts)]
        ymles.append(ymle)

        if shift:
            centers = np.array([(y0 + y1) / 2 for (y0, y1) in ybuckets[i]])
            closest_idx = np.argmin(np.abs(centers - ymle))
            shift = ymle - centers[closest_idx]
            shifted = [(y0 + shift, y1 + shift) for (y0, y1) in ybuckets[i]]
            new_ybuckets.append(shifted)
        else:
            new_ybuckets.append(ybuckets[i])

    return new_ybuckets, ymles

def clip_categories(df, xbuckets, ybuckets):
    ymin, ymax = df.index.min(), df.index.max()
    clipped_ybuckets = []
    for i, _ in enumerate(xbuckets):
        col_buckets = []
        for (y0, y1) in ybuckets[i]:
            # drop if completely outside
            if y1 <= ymin or y0 >= ymax:
                continue
            # clip to bounds
            y0c = max(y0, ymin)
            y1c = min(y1, ymax)
            if y1c > y0c:
                col_buckets.append((y0c, y1c))
        clipped_ybuckets.append(col_buckets)
    return clipped_ybuckets


def category_labels(xbuckets, ybuckets, ymles,correct_bias = True):
    nx = len(xbuckets)
    if correct_bias: 
        target = ymles
    else:
        target = [(x0 + x1) / 2 for (x0, x1) in xbuckets]
    
    xlabels = np.arange(nx)
    ylabels = []
    for i in range(nx):
        ybuckets_i = ybuckets[i]
        target_i = target[i]
        centers = np.array([(y0 + y1) / 2 for (y0, y1) in ybuckets_i])
        closest_idx = np.argmin(np.abs(centers - target_i))
        ylabels.append(np.arange(len(ybuckets_i))-closest_idx)
    return xlabels, ylabels

def aggregate_categories(df, xbuckets, ybuckets, xlabels, ylabels):
    x_vals = df.columns.values
    y_vals = df.index.values

    rows = sorted(set(np.concatenate(ylabels)))
    out = pd.DataFrame(0.0, index=rows, columns=xlabels)

    for i, (xs, xe) in enumerate(xbuckets):
        # x mask once per column
        xmask = (x_vals >= xs) & (x_vals < xe)

        for (y0, y1), yl in zip(ybuckets[i], ylabels[i]):
            ymask = (y_vals >= y0) & (y_vals < y1)

            val = df.loc[ymask, xmask].values.sum()
            out.loc[yl, xlabels[i]] += val

    return out.sort_index()

def plot_categories(df, xbuckets, ybuckets, xlabels, ylabels):
    fig, ax = plt.subplots()

    ax.imshow(df.values, origin='lower', aspect='auto', cmap='viridis')

    x_vals = df.columns.values
    y_vals = df.index.values

    for i, (xs, xe) in enumerate(xbuckets):
        for j, (y0, y1) in enumerate(ybuckets[i]):
            is_center = ylabels[i][j] == 0
            # map values -> indices
            x0 = np.searchsorted(x_vals, xs)
            x1 = np.searchsorted(x_vals, xe)
            y0i = np.searchsorted(y_vals, y0)
            y1i = np.searchsorted(y_vals, y1)

            ax.add_patch(plt.Rectangle(
                (x0, y0i),
                x1 - x0,
                y1i - y0i,
                fill=False,
                edgecolor='yellow' if is_center else 'red',
                linewidth=1
            ))

    plt.show()


# ---------------------------------------------------------------

if __name__ == "__main__":
    df = pd.read_pickle("histograms/kenya_sample.pkl")
    df.columns = df.columns.droplevel(0)
    # Ensure numeric index/columns
    df.index = df.index.astype(float)
    df.columns = df.columns.astype(float)

    pmin = 0
    pmax = 8
    df = df.loc[pmin:pmax, pmin:pmax]

    xbuckets, ybuckets = category_grid(ncategories=3, width=2, gap=0.2)
    ybuckets, ymles = recenter_categories(df, xbuckets, ybuckets, shift=True)
    ybuckets = clip_categories(df, xbuckets, ybuckets)
    xlabels, ylabels = category_labels(xbuckets, ybuckets, ymles, correct_bias=True)

    plot_categories(np.log(df), xbuckets, ybuckets, xlabels, ylabels)
    agg_df = aggregate_categories(df, xbuckets, ybuckets, xlabels, ylabels)
    import pdb; pdb.set_trace()


    precip_range = [0, 15]
    # clip df to precip range on both axes
    df = df.loc[precip_range[0]:precip_range[1], precip_range[0]:precip_range[1]]
    use_weight_mask = True
    rectilinear = False
    ncat = 10
    gap = 2

    x_vals = df.columns.values
    y_vals = df.index.values

    pmin, pmax = np.min(x_vals), np.max(x_vals)

    # --- 1. Build x bucket boundaries with gaps ---
    nbins = len(x_vals)
    total_gap = gap * (ncat - 1)
    usable_bins = nbins - total_gap
    bins_per_cat = usable_bins // ncat

    x_buckets = []
    start = 0
    for i in range(ncat):
        if start < nbins:
            end = min(start + bins_per_cat, nbins)
            x_buckets.append((start, end))
            start = end + gap

    y_buckets, center_bin_idxs = get_y_buckets(x_buckets, bins_per_cat, gap, rectilinear=rectilinear)
    show_buckets(np.log(df), x_buckets, y_buckets, center_bin_idxs)
    import pdb; pdb.set_trace()

    # --- 3. Aggregate into new grid ---
    result = np.zeros((ncat, ncat))

    for i, (xs, xe) in enumerate(x_buckets):
        for j, (ys, ye) in enumerate(y_buckets):
            sub = df.iloc[ys:ye, xs:xe]
            result[j, i] = sub.values.sum()

    # --- 4. Wrap result in DataFrame for readability ---
    out_df = pd.DataFrame(
        result,
        index=[f"ycat_{i}" for i in range(ncat)],
        columns=[f"xcat_{i}" for i in range(ncat)],
    )

    print(out_df)