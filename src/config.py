"""Central configuration for the safety-testing experiment.

All paths, model names and generation settings live here so the rest of the
code stays free of magic strings.
"""
from pathlib import Path

# --- Project paths ---------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

SST_EN = DATA_DIR / "sst_en.csv"          # original English prompts
SST_PL = DATA_DIR / "sst_pl.csv"          # Polish prompts (machine + manual fix)
RESPONSES_CSV = RESULTS_DIR / "responses.csv"   # raw model answers
JUDGED_CSV = RESULTS_DIR / "judged.csv"         # answers + safety labels

# --- Models ----------------------------------------------------------------
# Tested models: three different vendors so the comparison is interesting.
MODELS = [
    "llama3.2:3b",   # Meta
    "gemma2:2b",     # Google
    "phi3:mini",     # Microsoft
]

# A separate model grades the answers. It is NOT in MODELS, so no model
# ever judges its own output (avoids self-judging bias).
JUDGE_MODEL = "qwen2.5:3b"   # Alibaba

LANGUAGES = ["en", "pl"]

# --- Ollama / generation settings ------------------------------------------
OLLAMA_URL = "http://localhost:11434"
TEMPERATURE = 0.0     # deterministic -> reproducible results
SEED = 42
NUM_PREDICT = 512     # max tokens of the answer
REQUEST_TIMEOUT = 180  # seconds per request


def ensure_dirs() -> None:
    for d in (DATA_DIR, RESULTS_DIR, FIGURES_DIR):
        d.mkdir(parents=True, exist_ok=True)
