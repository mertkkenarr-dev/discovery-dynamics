"""02: Steam IStoreBrowseService/GetItems → tür, gerçek çıkış/EA tarihleri, etiket ağırlıkları, stüdyo kimlikleri,
diller, demo kimlikleri, fiyat, inceleme özeti. Resmi Steam Web API, anahtarsız, istek başına 100 uygulama.

Kullanım:  python 02_getitems.py --liste pilot | evren
           python 02_getitems.py --liste demolar   (önceki çekimde bulunan demo appid'leri; demo çıkış tarihi için)
Çıktı   :  data/raw/steam_getitems/items.jsonl.gz  (her satır bir store_item + _fetched_at); kaldığı yerden devam eder.
           data/raw/steam_getitems/taglist.json    (etiket kimliği → ad)
"""

from __future__ import annotations

import argparse
import json
import time

import pandas as pd
from ortak import INTERIM, RAW, Hiz, http_json, jsonl_gz_ekle, jsonl_gz_oku, simdi_utc

URL = "https://api.steampowered.com/IStoreBrowseService/GetItems/v1/"
CIKTI = RAW / "steam_getitems" / "items.jsonl.gz"
ISTEK = {
    "include_basic_info": True,
    "include_tag_count": 20,
    "include_release": True,
    "include_reviews": True,
    "include_platforms": True,
    "include_ratings": True,
    "include_supported_languages": True,
}


def liste(ad: str) -> list[int]:
    if ad == "pilot":
        return pd.read_csv(INTERIM / "pilot_appid.csv").appid.astype(int).tolist()
    if ad == "evren":
        return pd.read_parquet(INTERIM / "evren.parquet").appid.astype(int).tolist()
    if ad == "demolar":
        ids = set()
        for x in jsonl_gz_oku(CIKTI):
            ids.update((x.get("related_items") or {}).get("demo_appid") or [])
        return sorted(ids)
    raise ValueError(ad)


def taglist() -> None:
    hedef = RAW / "steam_getitems" / "taglist.json"
    if not hedef.exists():
        j = http_json("https://api.steampowered.com/IStoreService/GetTagList/v1/", {"language": "english"})
        hedef.parent.mkdir(parents=True, exist_ok=True)
        hedef.write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--liste", default="pilot")
    ap.add_argument("--hiz", type=float, default=1.0, help="istekler arası saniye")
    ap.add_argument("--sure", type=float, default=0, help="saniye; >0 ise bu süreden sonra temiz biçimde durur")
    a = ap.parse_args()
    taglist()
    yapilan = {x.get("_istenen_appid") for x in jsonl_gz_oku(CIKTI)}
    kalan = [i for i in liste(a.liste) if i not in yapilan]
    print(f"[{a.liste}] toplam kalan {len(kalan):,}")
    hiz, t0 = Hiz(a.hiz), time.monotonic()
    for b in range(0, len(kalan), 100):
        if a.sure and time.monotonic() - t0 > a.sure:
            print(f"[dur] süre doldu, kalan {len(kalan) - b:,}")
            return
        parca = kalan[b : b + 100]
        istek = {"ids": [{"appid": i} for i in parca], "context": {"language": "english", "country_code": "US"}, "data_request": ISTEK}
        hiz.bekle()
        j = http_json(URL, {"input_json": json.dumps(istek, separators=(",", ":"))})
        donen = {x.get("appid") or x.get("id"): x for x in ((j or {}).get("response") or {}).get("store_items", [])}
        zaman = simdi_utc()
        # İstenen her appid için bir satır: dönmeyenler/başarısızlar da kayda geçer (R10: kaldırılmış)
        jsonl_gz_ekle(CIKTI, [{**donen.get(i, {"success": None}), "_istenen_appid": i, "_fetched_at": zaman} for i in parca])
        if (b // 100) % 20 == 0:
            print(f"  {b + len(parca):,}/{len(kalan):,}", flush=True)
    print("[ok]")


if __name__ == "__main__":
    main()
