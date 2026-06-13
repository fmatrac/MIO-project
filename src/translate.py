"""Machine-translate the English prompts to Polish (EN -> PL).

Uses Google Translate via deep-translator (no API key needed). The output is
saved to data/sst_pl.csv and is afterwards reviewed/corrected by hand. Each
row keeps the original English prompt in `prompt_en` for reference.
"""
import time

import pandas as pd
from deep_translator import GoogleTranslator

import config


def main() -> None:
    config.ensure_dirs()
    df = pd.read_csv(config.SST_EN)
    translator = GoogleTranslator(source="en", target="pl")

    pl_prompts = []
    for i, text in enumerate(df["prompt"], 1):
        pl = translator.translate(text)
        pl_prompts.append(pl)
        print(f"[{i:>3}/{len(df)}] {text[:45]!r} -> {pl[:45]!r}")
        time.sleep(0.2)  # be gentle with the free endpoint

    out = df.copy()
    out["prompt_en"] = out["prompt"]
    out["prompt"] = pl_prompts
    out.to_csv(config.SST_PL, index=False)
    print(f"\nSaved {len(out)} Polish prompts to {config.SST_PL}")


if __name__ == "__main__":
    main()
