"""03: Steam inceleme grafiği (appreviewhistogram) → oyun başına ömür boyu aylık/haftalık olumlu-olumsuz seriler.

Kapsam : GetItems'ta type=0 (oyun) olan ve listede yer alan uygulamalar.
Kullanım: python 03_histogram.py --liste pilot | evren  [--paralel 4] [--min-inceleme 10]
Kısaltma: GetItems'taki ömür boyu inceleme sayısı --min-inceleme'nin altındaysa grafik çekilmez. Bu oyunlar için
         reviews_365 ≤ ömür boyu toplam < 10 olduğundan kademe (T0) ve hit=0 kesin bilinir; sürekli değer olarak
         ömür boyu toplam kullanılır (hata < 10 inceleme). Bkz. ANALIZ_PLANI.md §6.
Çıktı  : data/raw/steam_histogram/histogram.jsonl.gz  (appid, results, _fetched_at); kaldığı yerden devam eder.
Tanım  : Bu uç noktanın saydığı incelemeler Steam puanına giren incelemelerdir (Steam'den satın alınanlara yakın;
         tüm incelemelerin ~%84–97'si). Bkz. ANALIZ_PLANI.md B7.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf

import pandas as pd
from ortak import INTERIM, RAW, ayarlar, http_json, ilk_steam_erisimi, jsonl_gz_ekle, jsonl_gz_oku, simdi_utc

CIKTI = RAW / "steam_histogram" / "histogram.jsonl.gz"
GETITEMS = RAW / "steam_getitems" / "items.jsonl.gz"
MIN_INCELEME = 10


def cek(appid: int) -> dict:
    j = http_json(f"https://store.steampowered.com/appreviewhistogram/{appid}", {"l": "english", "review_score_preference": 0})
    return {"appid": appid, "success": (j or {}).get("success"), "results": (j or {}).get("results"), "_fetched_at": simdi_utc()}


def hedefler(ad: str) -> list[int]:
    cfg = ayarlar()
    bas = pd.Timestamp(str(cfg["kohort"]["baslangic"])).timestamp()
    oyunlar = {
        x["_istenen_appid"]
        for x in jsonl_gz_oku(GETITEMS)
        if x.get("success") == 1
        and x.get("type") == 0
        # Üst sınır yok: Steam yeniden yayında tarihi sıfırlayabiliyor (Enshrouded 2024 → 2026); gerçek tarih histogramdan
        # bulunur ve kohort 11_sonuc.py'de düzeltilmiş tarihle belirlenir (T14). Alt sınır güvenli: düzeltme tarihi sadece geri çeker.
        and bas <= (ilk_steam_erisimi(x) or 0)
        and (((x.get("reviews") or {}).get("summary_filtered") or {}).get("review_count") or 0) >= MIN_INCELEME
    }
    if ad == "pilot":
        aday = pd.read_csv(INTERIM / "pilot_appid.csv").appid.astype(int).tolist()
    else:
        aday = pd.read_parquet(INTERIM / "evren.parquet").appid.astype(int).tolist()
    return [i for i in aday if i in oyunlar]


def main() -> None:
    global MIN_INCELEME
    ap = argparse.ArgumentParser()
    ap.add_argument("--liste", default="pilot")
    ap.add_argument("--paralel", type=int, default=4, help="eşzamanlı istek (pilotta 8'e kadar 429 görülmedi)")
    ap.add_argument("--min-inceleme", type=int, default=10)
    a = ap.parse_args()
    MIN_INCELEME = a.min_inceleme
    yapilan = {x["appid"] for x in jsonl_gz_oku(CIKTI)}
    kalan = [i for i in hedefler(a.liste) if i not in yapilan]
    print(f"[{a.liste}] kalan {len(kalan):,}", flush=True)
    for b in range(0, len(kalan), 200):
        with cf.ThreadPoolExecutor(a.paralel) as ex:
            jsonl_gz_ekle(CIKTI, list(ex.map(cek, kalan[b : b + 200])))
        print(f"  {min(b + 200, len(kalan)):,}/{len(kalan):,}", flush=True)
    print("[ok]")


if __name__ == "__main__":
    main()
