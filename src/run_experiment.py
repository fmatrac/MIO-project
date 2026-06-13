"""Ask every model each prompt, in English and in Polish.

For each (model, language, prompt) we record the model's answer. The script is
resumable: if results/responses.csv already has a row for a given
(model, lang, id), that combination is skipped. So a crash or Ctrl-C does not
lose work - just run the script again.
"""
import csv

import pandas as pd

import config
import ollama_client

FIELDS = ["id", "harm_area", "category", "lang", "model", "prompt", "response"]


def load_prompts() -> list[dict]:
    """Return one record per (lang, prompt)."""
    records = []
    for lang, path in (("en", config.SST_EN), ("pl", config.SST_PL)):
        df = pd.read_csv(path)
        for _, r in df.iterrows():
            records.append(
                {
                    "id": r["id"],
                    "harm_area": r["harm_area"],
                    "category": r["category"],
                    "lang": lang,
                    "prompt": r["prompt"],
                }
            )
    return records


def already_done() -> set[tuple]:
    if not config.RESPONSES_CSV.exists():
        return set()
    df = pd.read_csv(config.RESPONSES_CSV)
    return set(zip(df["model"], df["lang"], df["id"]))


def main() -> None:
    config.ensure_dirs()
    prompts = load_prompts()
    done = already_done()

    new_file = not config.RESPONSES_CSV.exists()
    f = open(config.RESPONSES_CSV, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    if new_file:
        writer.writeheader()

    total = len(config.MODELS) * len(prompts)
    step = 0
    for model in config.MODELS:
        for rec in prompts:
            step += 1
            key = (model, rec["lang"], rec["id"])
            if key in done:
                continue
            try:
                answer = ollama_client.chat(model, rec["prompt"])
            except Exception as e:  # keep going even if one call fails
                answer = f"<ERROR: {e}>"
            writer.writerow(
                {
                    "id": rec["id"],
                    "harm_area": rec["harm_area"],
                    "category": rec["category"],
                    "lang": rec["lang"],
                    "model": model,
                    "prompt": rec["prompt"],
                    "response": answer,
                }
            )
            f.flush()
            print(f"[{step:>4}/{total}] {model} | {rec['lang']} | {rec['id']}")
    f.close()
    print(f"\nDone. Responses saved to {config.RESPONSES_CSV}")


if __name__ == "__main__":
    main()
