"""00: Açık veri setlerini indirir → data/raw/<kaynak>/<sürüm>/ + manifesto.

Şimdilik: FronkonGames/steam-games-dataset (Hugging Face, MIT), yalnız Parquet (~192 MB).
Büyük setler buraya eklenmeden önce boyutu sorulur (bkz. docs/VERI_KATALOGU.md).
"""

from __future__ import annotations

import shutil

import os

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")  # xet CDN yerine düz HTTP indirme

from huggingface_hub import HfApi, hf_hub_download  # noqa: E402
from ortak import RAW, manifeste_ekle  # noqa: E402

SETLER = [
    {
        "kaynak": "fronkongames",
        "repo": "FronkonGames/steam-games-dataset",
        "dosya": "data/train-00000-of-00001.parquet",
        "lisans": "MIT (HF etiketi)",
    },
    {
        "kaynak": "z02z",
        "repo": "Z02Z/steam-games-dataset",
        "dosya": "data/train-00000-of-00001.parquet",
        "lisans": "CC BY 4.0 (HF etiketi)",
    },
]


def main() -> None:
    api = HfApi()
    for s in SETLER:
        bilgi = api.dataset_info(s["repo"])
        surum = bilgi.last_modified.strftime("%Y-%m-%d")
        hedef_klasor = RAW / s["kaynak"] / surum
        hedef = hedef_klasor / "games.parquet"
        if hedef.exists():
            print(f"[atla] {hedef} zaten var")
            continue
        hedef_klasor.mkdir(parents=True, exist_ok=True)
        yol = hf_hub_download(s["repo"], s["dosya"], repo_type="dataset", revision=bilgi.sha)
        shutil.copyfile(yol, hedef)
        url = f"https://huggingface.co/datasets/{s['repo']}/resolve/{bilgi.sha}/{s['dosya']}"
        manifeste_ekle(s["kaynak"], hedef, url, s["lisans"], f"HF commit {bilgi.sha[:10]}, son değişiklik {surum}")
        print(f"[ok] {hedef} ({hedef.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
