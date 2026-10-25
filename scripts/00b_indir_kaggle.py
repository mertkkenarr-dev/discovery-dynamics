"""00b: Küçük Kaggle setlerini indirir → data/raw/kaggle_<sahip>__<set>/<indirme tarihi>/ + manifesto.

Gereken: .env içinde KAGGLE_API_TOKEN ve PATH'te `kaggle` CLI (>=1.8). Farklı bir komut için KAGGLE_BIN.
Büyük setler (>500 MB) burada yok; eklemeden önce sorulur.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from datetime import date

from dotenv import load_dotenv
from ortak import KOK, RAW, manifeste_ekle

SETLER = [
    ("lunthu/steam-monthly-average-players", "Kaggle sayfasında belirtilmemiş"),
    ("michau96/popularity-of-games-on-steam", "Kaggle sayfasında belirtilmemiş"),
    ("rankirsh/evolution-of-top-games-on-twitch", "Kaggle sayfasında belirtilmemiş"),
]


def main() -> None:
    load_dotenv(KOK / ".env")
    kaggle = shlex.split(os.environ.get("KAGGLE_BIN", "kaggle"))
    bugun = date.today().isoformat()
    for ref, lisans in SETLER:
        klasor = RAW / ("kaggle_" + ref.replace("/", "__")) / bugun
        if klasor.exists() and any(klasor.iterdir()):
            print(f"[atla] {ref}")
            continue
        klasor.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([*kaggle, "datasets", "download", "-d", ref, "-p", tmp, "--unzip", "-q"], check=True)
            subprocess.run([*kaggle, "datasets", "metadata", "-p", tmp, ref], check=True, capture_output=True)
            meta = json.loads((__import__("pathlib").Path(tmp) / "dataset-metadata.json").read_text())
            lisans = ", ".join(x.get("name", "?") for x in meta.get("licenses", [])) or lisans
            for f in sorted(__import__("pathlib").Path(tmp).rglob("*")):
                if f.is_file() and not f.name.endswith((".zip", ".kaggle-partial")) and f.name != "dataset-metadata.json":
                    hedef = klasor / f.relative_to(tmp)
                    hedef.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, hedef)
                    manifeste_ekle("kaggle:" + ref, hedef, f"https://www.kaggle.com/datasets/{ref}", lisans)
        print(f"[ok] {ref}: {[f.name for f in klasor.rglob('*') if f.is_file()]}")


if __name__ == "__main__":
    main()
