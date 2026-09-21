"""Listet die am KISSKI-Endpunkt freigeschalteten Modelle (braucht KISSKI_API_KEY in .env).

uv run scripts/list_models.py
"""

from pathlib import Path

from openai import OpenAI

from promptner.config import get_settings
from promptner.llm import list_model_ids


def main() -> int:
    s = get_settings()
    sdk = OpenAI(base_url=s.llm_base_url, api_key=s.require_api_key())
    ids = list_model_ids(sdk)
    out = Path(s.results_dir) / "models.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(ids) + "\n", encoding="utf-8")
    print(f"{len(ids)} Modelle -> {out}")
    print("\n".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
