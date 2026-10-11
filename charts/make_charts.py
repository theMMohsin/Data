"""Generate PNG charts from the World Happiness Report CSVs (2015-2019).

Run from the repo root:  python3 charts/make_charts.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "World_Happiness_Report"
OUT = ROOT / "charts"
YEARS = [2015, 2016, 2017, 2018, 2019]

# Palette and chrome (light mode)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RED = "#e34948"
BLUE_LIGHT = "#9ec5f4"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "axes.edgecolor": AXIS,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 26,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ---------------------------------------------------------------- load + clean
NAME_FIX = {
    "Hong Kong S.A.R., China": "Hong Kong",
    "Taiwan Province of China": "Taiwan",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "North Cyprus": "Northern Cyprus",
    "North Macedonia": "Macedonia",
    "Somaliland Region": "Somaliland region",
}
COLS_1516 = {"Happiness Score": "Score", "Economy (GDP per Capita)": "GDP", "Family": "Social",
             "Health (Life Expectancy)": "Health", "Trust (Government Corruption)": "Trust"}
COLS_17 = {"Happiness.Score": "Score", "Economy..GDP.per.Capita.": "GDP", "Family": "Social",
           "Health..Life.Expectancy.": "Health", "Trust..Government.Corruption.": "Trust"}
COLS_1819 = {"Country or region": "Country", "GDP per capita": "GDP", "Social support": "Social",
             "Healthy life expectancy": "Health", "Freedom to make life choices": "Freedom",
             "Perceptions of corruption": "Trust"}
FACTORS = ["GDP", "Social", "Health", "Freedom", "Trust", "Generosity"]
FACTOR_LABELS = {"GDP": "GDP per capita", "Social": "Social support", "Health": "Healthy life expectancy",
                 "Freedom": "Freedom to make choices", "Trust": "Trust (low corruption)", "Generosity": "Generosity"}

frames = []
for year, cols in zip(YEARS, [COLS_1516, COLS_1516, COLS_17, COLS_1819, COLS_1819]):
    df = pd.read_csv(DATA / f"{year}.csv").rename(columns=cols)
    df["Country"] = df["Country"].replace(NAME_FIX)
    df["Year"] = year
    frames.append(df[["Country", "Year", "Score"] + FACTORS])
data = pd.concat(frames, ignore_index=True)

region = (pd.concat([pd.read_csv(DATA / "2015.csv"), pd.read_csv(DATA / "2016.csv")])
          .assign(Country=lambda d: d["Country"].replace(NAME_FIX))
          .drop_duplicates("Country").set_index("Country")["Region"])
region["Gambia"] = "Sub-Saharan Africa"
data["Region"] = data["Country"].map(region)

scores = data.pivot(index="Country", columns="Year", values="Score")
y2019 = data[data["Year"] == 2019].copy()


def source_note(fig, text="Source: World Happiness Report 2015–2019"):
    fig.text(0.01, 0.01, text, color=MUTED, fontsize=8, ha="left", va="bottom")


def subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK_2, fontsize=10, va="bottom")


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ------------------------------------------------------- 1. score distribution
fig, ax = plt.subplots(figsize=(9, 5))
bins = np.arange(2.5, 8.01, 0.25)
ax.hist(y2019["Score"], bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=2)
mean = y2019["Score"].mean()
ax.axvline(mean, color=INK_2, linewidth=1.2, linestyle="--")
ax.set_ylim(0, 20)
ax.text(mean + 0.05, 19.5, f"Average {mean:.2f}", color=INK_2, va="top")
ax.set_title("Most countries score between 4.5 and 6.5")
subtitle(ax, "Distribution of happiness scores, 156 countries, 2019 (0–10 scale)")
ax.set_xlabel("Happiness score")
ax.set_ylabel("Number of countries")
ax.grid(axis="x", visible=False)
source_note(fig)
save(fig, "01_score_distribution_2019.png")

# ------------------------------------------------- 2. region averages, 2015 vs 2019
reg = (data[data["Year"].isin([2015, 2019])].groupby(["Region", "Year"])["Score"].mean()
       .unstack().sort_values(2019))
fig, ax = plt.subplots(figsize=(9, 5.5))
yy = np.arange(len(reg))
ax.hlines(yy, reg[2015], reg[2019], color=AXIS, linewidth=2, zorder=1)
ax.scatter(reg[2015], yy, s=70, color=BLUE_LIGHT, edgecolor=SURFACE, linewidth=2, zorder=2, label="2015")
ax.scatter(reg[2019], yy, s=70, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3, label="2019")
for i, (a, b) in enumerate(zip(reg[2015], reg[2019])):
    d = b - a
    ax.text(max(a, b) + 0.08, i, f"{d:+.2f}", va="center", fontsize=9, color=INK_2)
ax.set_yticks(yy, reg.index, color=INK)
ax.set_xlim(3.9, 7.7)
ax.set_xlabel("Average happiness score")
ax.grid(axis="y", visible=False)
ax.legend(loc="upper left", frameon=False, labelcolor=INK_2)
ax.set_title("A 3-point gap between regions that barely moved")
subtitle(ax, "Average happiness score by region, 2015 vs 2019 (label = change)")
source_note(fig)
save(fig, "02_region_averages_2015_vs_2019.png")

# ----------------------------------------------- 3. biggest risers & fallers
full = scores.dropna()
change = (full[2019] - full[2015]).sort_values()
movers = pd.concat([change.head(8), change.tail(8)])
fig, ax = plt.subplots(figsize=(9, 6.5))
colors = [RED if v < 0 else BLUE for v in movers]
ax.barh(movers.index, movers.values, color=colors, height=0.7, edgecolor=SURFACE, linewidth=1)
for i, v in enumerate(movers.values):
    ax.text(v + (0.04 if v > 0 else -0.04), i, f"{v:+.2f}", va="center",
            ha="left" if v > 0 else "right", fontsize=9, color=INK_2)
ax.axvline(0, color=AXIS, linewidth=1)
ax.set_xlim(-2.5, 2.0)
ax.tick_params(axis="y", colors=INK)
ax.set_xlabel("Change in happiness score, 2015 → 2019")
ax.grid(axis="y", visible=False)
ax.set_title("Venezuela fell twice as far as any other country")
subtitle(ax, "8 biggest falls and 8 biggest rises among the 146 countries in all five reports")
source_note(fig)
save(fig, "03_biggest_risers_fallers.png")

# ------------------------------------------------ 4. country trends (line chart)
focus = [("Venezuela", ORANGE), ("India", YELLOW), ("Benin", BLUE), ("Ivory Coast", AQUA)]
label_nudge = {"Ivory Coast": 0.09, "Benin": -0.03, "Venezuela": -0.1}
fig, ax = plt.subplots(figsize=(9, 5.5))
for name, color in focus:
    s = scores.loc[name]
    ax.plot(YEARS, s.values, color=color, linewidth=2, marker="o", markersize=7,
            markeredgecolor=SURFACE, markeredgewidth=2, label=name)
    ax.text(2019.12, s[2019] + label_nudge.get(name, 0), f"{name}  {s[2019]:.2f}", va="center", color=INK, fontsize=10)
    ax.text(2014.88, s[2015], f"{s[2015]:.2f}", va="center", ha="right", color=INK_2, fontsize=9)
world = data.groupby("Year")["Score"].mean()
ax.plot(YEARS, world.values, color=MUTED, linewidth=1.5, linestyle="--", label="World average")
ax.text(2019.12, world[2019] + 0.12, "World avg", va="center", color=MUTED, fontsize=9)
ax.set_xticks(YEARS)
ax.set_xlim(2014.6, 2020.1)
ax.set_ylim(3, 7.2)
ax.set_ylabel("Happiness score")
ax.grid(axis="x", visible=False)
ax.legend(loc="upper right", frameon=False, labelcolor=INK_2)
ax.set_title("Venezuela and India slid every year; Benin and Ivory Coast climbed")
subtitle(ax, "Happiness score by year")
source_note(fig)
save(fig, "04_country_trends.png")

# ------------------------------------------------ 5. factor correlations
corr = y2019[FACTORS].corrwith(y2019["Score"]).sort_values()
fig, ax = plt.subplots(figsize=(9, 4.8))
labels = [FACTOR_LABELS[f] for f in corr.index]
ax.barh(labels, corr.values, color=BLUE, height=0.6)
for i, v in enumerate(corr.values):
    ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=10, color=INK_2)
ax.set_xlim(0, 1)
ax.tick_params(axis="y", colors=INK)
ax.set_xlabel("Correlation with happiness score (Pearson r)")
ax.grid(axis="y", visible=False)
ax.set_title("Wealth, social support and health track happiness; generosity doesn't")
subtitle(ax, "Correlation of each factor with happiness score, 2019")
source_note(fig)
save(fig, "05_factor_correlations_2019.png")

# ------------------------------------------------ 6. GDP vs happiness scatter
slope, intercept = np.polyfit(y2019["GDP"], y2019["Score"], 1)
y2019["Residual"] = y2019["Score"] - (slope * y2019["GDP"] + intercept)
r2 = np.corrcoef(y2019["GDP"], y2019["Score"])[0, 1] ** 2
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(y2019["GDP"], y2019["Score"], s=40, color=BLUE, alpha=0.75, edgecolor=SURFACE, linewidth=1)
xs = np.linspace(0, y2019["GDP"].max(), 50)
ax.plot(xs, slope * xs + intercept, color=INK_2, linewidth=1.2, linestyle="--",
        label=f"Trend from GDP alone (R² = {r2:.2f})")
ax.legend(loc="lower right", frameon=False, labelcolor=INK_2)
labelled = pd.concat([y2019.nlargest(4, "Residual"), y2019.nsmallest(4, "Residual")])
offsets = {"Costa Rica": (-10, 8), "Finland": (-10, 8), "Somalia": (8, 4), "Guatemala": (-10, 10),
           "Botswana": (8, -10), "Syria": (8, -4), "Iran": (8, -4), "Iraq": (8, -12)}
for _, row in labelled.iterrows():
    dx, dy = offsets.get(row["Country"], (6, 6))
    ax.annotate(row["Country"], (row["GDP"], row["Score"]), xytext=(dx, dy), textcoords="offset points",
                fontsize=9, color=INK, ha="right" if dx < 0 else "left")
    ax.scatter(row["GDP"], row["Score"], s=60, facecolor="none", edgecolor=INK, linewidth=1.2)
ax.set_xlabel("GDP per capita (contribution to score)")
ax.set_ylabel("Happiness score")
ax.set_title("Richer countries are happier, but not always")
subtitle(ax, "Each dot is a country, 2019. Circled = furthest above or below the GDP trend")
source_note(fig)
save(fig, "06_gdp_vs_happiness_2019.png")

# ------------------------------------------------ 7. top 10 rank table (heatmap)
top_countries = (data[data["Year"] == 2019].nlargest(10, "Score")["Country"].tolist()
                 + ["Australia"])
ranks = data.assign(Rank=data.groupby("Year")["Score"].rank(ascending=False, method="min"))
rank_tbl = ranks.pivot(index="Country", columns="Year", values="Rank").loc[top_countries]
fig, ax = plt.subplots(figsize=(8, 6))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("blues", ["#0d366b", "#2a78d6", "#cde2fb"])
ax.imshow(rank_tbl.values, cmap=cmap, vmin=1, vmax=15, aspect="auto")
for i in range(rank_tbl.shape[0]):
    for j in range(rank_tbl.shape[1]):
        v = int(rank_tbl.iat[i, j])
        ax.text(j, i, v, ha="center", va="center", fontsize=11,
                color="white" if v <= 7 else INK, fontweight="bold" if v == 1 else "normal")
ax.set_xticks(range(len(YEARS)), YEARS)
ax.set_yticks(range(len(top_countries)), top_countries, color=INK)
ax.tick_params(length=0)
ax.grid(False)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks(np.arange(-0.5, len(YEARS)), minor=True)
ax.set_yticks(np.arange(-0.5, len(top_countries)), minor=True)
ax.grid(which="minor", color=SURFACE, linewidth=2)
ax.tick_params(which="minor", length=0)
ax.set_title("The same nine countries hold the top 10 every year")
subtitle(ax, "World rank by year, 2019 top 10 plus Australia (darker = higher)")
source_note(fig)
save(fig, "07_top10_rank_heatmap.png")
