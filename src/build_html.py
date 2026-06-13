"""Build a single, self-contained HTML version of the report.

Images are embedded as base64 so the file is fully portable (one file, works
offline). Open it in a browser and use "Print -> Save as PDF" to get a PDF for
the MS Teams submission.
"""
import base64
import re
from pathlib import Path

import markdown

import config

MD_PATH = config.ROOT / "sprawozdanie" / "sprawozdanie.md"
HTML_PATH = config.ROOT / "sprawozdanie" / "sprawozdanie.html"

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 820px;
       margin: 2rem auto; line-height: 1.5; color: #1a1a1a; padding: 0 1rem; }
h1 { font-size: 1.9rem; border-bottom: 3px solid #4C72B0; padding-bottom: .3rem; }
h2 { font-size: 1.4rem; margin-top: 2rem; color: #2a3f5f;
     border-bottom: 1px solid #ccc; padding-bottom: .2rem; }
h3 { font-size: 1.1rem; color: #2a3f5f; }
table { border-collapse: collapse; margin: 1rem 0; width: 100%; font-size: .95rem; }
th, td { border: 1px solid #bbb; padding: .4rem .6rem; text-align: left; }
th { background: #eef2f8; }
img { max-width: 100%; display: block; margin: 1rem auto;
      border: 1px solid #ddd; border-radius: 4px; }
blockquote { border-left: 4px solid #DD8452; margin: 1rem 0; padding: .3rem 1rem;
             background: #fdf6f0; color: #333; }
code { background: #f4f4f4; padding: .1rem .3rem; border-radius: 3px; }
pre { background: #f4f4f4; padding: .8rem; border-radius: 5px; overflow-x: auto; }
pre code { background: none; }
@media print { body { margin: 0; max-width: none; } h2 { page-break-after: avoid; } }
"""


def embed_images(md_text: str) -> str:
    """Replace ![alt](path) with ![alt](data:image/png;base64,...)."""
    def repl(m):
        alt, rel = m.group(1), m.group(2)
        img_path = (MD_PATH.parent / rel).resolve()
        if not img_path.exists():
            return m.group(0)
        data = base64.b64encode(img_path.read_bytes()).decode()
        return f"![{alt}](data:image/png;base64,{data})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, md_text)


def main() -> None:
    md_text = embed_images(MD_PATH.read_text(encoding="utf-8"))
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = (
        f"<!DOCTYPE html><html lang='pl'><head><meta charset='utf-8'>"
        f"<title>Sprawozdanie - bezpieczenstwo LLM</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"Saved {HTML_PATH} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
