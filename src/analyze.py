"""Aggregate the labelled answers into tables and figures.

Outputs (under results/):
  - summary_by_model_lang.csv      unsafe & refusal rate per model and language
  - summary_by_harm_area_lang.csv  unsafe rate per harm area and language
  - summary_by_model_harm_lang.csv detailed model x harm x language
  - figures/*.png                  bar charts used in the report
Also prints a short text summary (incl. the English vs Polish gap).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

LANG_NAME = {"en": "English", "pl": "Polish"}
COLORS = {"en": "#4C72B0", "pl": "#DD8452"}


def pct(x) -> float:
    return round(100.0 * float(x), 1)


def load() -> pd.DataFrame:
    df = pd.read_csv(config.JUDGED_CSV)
    df["unsafe"] = df["unsafe"].astype(bool)
    df["is_refusal"] = df["is_refusal"].astype(bool)
    return df


def make_summaries(df: pd.DataFrame) -> dict:
    by_model_lang = (
        df.groupby(["model", "lang"])
        .agg(n=("unsafe", "size"),
             unsafe_n=("unsafe", "sum"),
             unsafe_rate=("unsafe", "mean"),
             refusal_rate=("is_refusal", "mean"))
        .reset_index()
    )
    by_model_lang["unsafe_rate"] = by_model_lang["unsafe_rate"].map(pct)
    by_model_lang["refusal_rate"] = by_model_lang["refusal_rate"].map(pct)
    by_model_lang.to_csv(config.RESULTS_DIR / "summary_by_model_lang.csv", index=False)

    by_harm = (
        df.groupby(["harm_area", "lang"])["unsafe"].mean().mul(100).round(1)
        .reset_index().rename(columns={"unsafe": "unsafe_rate"})
    )
    by_harm.to_csv(config.RESULTS_DIR / "summary_by_harm_area_lang.csv", index=False)

    by_model_harm = (
        df.groupby(["model", "harm_area", "lang"])["unsafe"].mean().mul(100).round(1)
        .reset_index().rename(columns={"unsafe": "unsafe_rate"})
    )
    by_model_harm.to_csv(config.RESULTS_DIR / "summary_by_model_harm_lang.csv", index=False)

    return {"model_lang": by_model_lang, "harm": by_harm, "model_harm": by_model_harm}


def grouped_bar(categories, en_vals, pl_vals, title, ylabel, fname, rotate=0):
    x = np.arange(len(categories))
    w = 0.38
    fig, ax = plt.subplots(figsize=(max(6, len(categories) * 1.5), 4.5))
    ax.bar(x - w / 2, en_vals, w, label="English", color=COLORS["en"])
    ax.bar(x + w / 2, pl_vals, w, label="Polish", color=COLORS["pl"])
    for i, (e, p) in enumerate(zip(en_vals, pl_vals)):
        ax.text(i - w / 2, e + 1, f"{e:.0f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + w / 2, p + 1, f"{p:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=rotate, ha="right" if rotate else "center")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(100, max(list(en_vals) + list(pl_vals)) + 8))
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / fname, dpi=130)
    plt.close(fig)


def heatmap(df: pd.DataFrame, lang: str, fname: str):
    sub = df[df["lang"] == lang]
    piv = sub.pivot_table(index="model", columns="harm_area",
                          values="unsafe", aggfunc="mean").mul(100)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    im = ax.imshow(piv.values, cmap="Reds", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels(piv.columns, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels(piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:.0f}", ha="center", va="center",
                    fontsize=8, color="black")
    ax.set_title(f"Unsafe rate (%) by model and harm area - {LANG_NAME[lang]}")
    fig.colorbar(im, ax=ax, label="unsafe %")
    fig.tight_layout()
    fig.savefig(config.FIGURES_DIR / fname, dpi=130)
    plt.close(fig)


def main() -> None:
    df = load()
    s = make_summaries(df)

    # Figure 1: unsafe rate per model, EN vs PL
    ml = s["model_lang"]
    models = config.MODELS
    en = [ml[(ml.model == m) & (ml.lang == "en")]["unsafe_rate"].values[0] for m in models]
    pl = [ml[(ml.model == m) & (ml.lang == "pl")]["unsafe_rate"].values[0] for m in models]
    grouped_bar(models, en, pl,
                "Unsafe-response rate by model and language",
                "Unsafe responses (%)", "fig1_unsafe_by_model_lang.png")

    # Figure 2: unsafe rate per harm area, EN vs PL (averaged over models)
    harm = s["harm"]
    areas = sorted(harm["harm_area"].unique())
    short = {a: a.replace(" and ", " &\n").replace(", ", ",\n") for a in areas}
    en_h = [harm[(harm.harm_area == a) & (harm.lang == "en")]["unsafe_rate"].values[0] for a in areas]
    pl_h = [harm[(harm.harm_area == a) & (harm.lang == "pl")]["unsafe_rate"].values[0] for a in areas]
    grouped_bar([short[a] for a in areas], en_h, pl_h,
                "Unsafe-response rate by harm area and language",
                "Unsafe responses (%)", "fig2_unsafe_by_harm_area_lang.png", rotate=0)

    # Figure 3: refusal rate per model, EN vs PL
    en_r = [ml[(ml.model == m) & (ml.lang == "en")]["refusal_rate"].values[0] for m in models]
    pl_r = [ml[(ml.model == m) & (ml.lang == "pl")]["refusal_rate"].values[0] for m in models]
    grouped_bar(models, en_r, pl_r,
                "Refusal rate (rule-based) by model and language",
                "Answers containing a refusal (%)", "fig3_refusal_by_model_lang.png")

    # Figure 4: heatmap model x harm area for Polish
    heatmap(df, "pl", "fig4_heatmap_model_harm_pl.png")
    heatmap(df, "en", "fig5_heatmap_model_harm_en.png")

    # text summary
    print("=" * 60)
    print("SUMMARY  (unsafe = model complied with a harmful prompt)")
    print("=" * 60)
    print(ml.to_string(index=False))
    overall = df.groupby("lang")["unsafe"].mean().mul(100).round(1)
    print("\nOverall unsafe rate:")
    print(f"  English: {overall.get('en', float('nan'))}%")
    print(f"  Polish : {overall.get('pl', float('nan'))}%")
    gap = overall.get("pl", 0) - overall.get("en", 0)
    print(f"  Polish - English gap: {gap:+.1f} percentage points")
    # judge vs rule-based agreement (sanity check on the judge):
    # the rule-based signal predicts "safe" when a refusal is detected, so it
    # should agree with judge=SAFE. i.e. unsafe == (not refusal).
    agreement = (df["unsafe"] == (~df["is_refusal"])).mean()
    print(f"\nAgreement: judge(UNSAFE) vs rule-based(no refusal): {pct(agreement)}%")
    print(f"\nFigures written to {config.FIGURES_DIR}")


if __name__ == "__main__":
    main()
