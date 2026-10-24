"""07: M8 örneklemi için tek tek Steam incelemeleri (appreviews) → günlük seri ve (M7 için) metin.

Kullanım: python 07_inceleme.py [--paralel 3] [--sinir N]      (13_yayinla'dan sonra; oyun_tablosu gerekir)
Örneklem: HIPOTEZLER 2026-10-24 H8 tanımı — analiz örneklemi, çıkış 2021-01-01–2024-06-30, reviews_365 tabakaları
          200–499 (150), 500–4.999 (200), 5.000–20.000 (50); tohum 20261024 → interim/m8_orneklem.csv
Çıktı   : raw/steam_inceleme/incelemeler.jsonl.gz — oyun başına bir satır (tamamlanınca yazılır; kesilirse oyun baştan çekilir).
Uç nokta: store.steampowered.com/appreviews/{appid}?json=1&filter=recent&language=all&purchase_type=all, 100/sayfa, imleçli.

⚠️ 2026-10-24: Bu uç nokta artık HTTP 302 ile mağaza ana sayfasına yönlendiriyor (kaldırılmış). Yeni IUserReviewsService/GetAppReviews
   yalnız son 30–365 günü veriyor ve F2P'de boş dönüyor → 2021–2024 için günlük seri alınamaz. Betik bu haliyle ÇALIŞMAZ; H8 kararı
   kullanıcıda (HIPOTEZLER değişiklik günlüğü). Örneklem dosyası (interim/m8_orneklem.csv) ileride kullanılmak üzere duruyor.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf

import numpy as np
import pandas as pd
from ortak import INTERIM, PROCESSED, RAW, Hiz, ayarlar, http_json, jsonl_gz_ekle, jsonl_gz_oku, simdi_utc

CIKTI = RAW / "steam_inceleme" / "incelemeler.jsonl.gz"
TABAKA = [(200, 499, 150), (500, 4999, 200), (5000, 20000, 50)]
ALANLAR = ("recommendationid", "timestamp_created", "voted_up", "language", "steam_purchase", "received_for_free", "written_during_early_access",
           "review", "votes_up")  # fmt: skip


def orneklem() -> pd.DataFrame:
    yol = INTERIM / "m8_orneklem.csv"
    if yol.exists():
        return pd.read_csv(yol)
    t = pd.read_parquet(PROCESSED / "oyun_tablosu.parquet")
    a = t[t.kohort & t.organik & t.reviews_365.notna() & ~t.seri_uretici & ~t.yetiskin & ~t.yazilim_suphe & ~t.listelenmemis]
    a = a[(a.cikis >= "2021-01-01") & (a.cikis < "2024-07-01")]
    rng = np.random.default_rng(20261024)
    secim = []
    for alt, ust, n in TABAKA:
        h = a[a.reviews_365.round().between(alt, ust)].sort_values("appid")
        secim.append(h.iloc[rng.choice(len(h), min(n, len(h)), replace=False)].assign(tabaka=f"{alt}-{ust}"))
    s = pd.concat(secim)[["appid", "ad", "cikis", "tam_surum_tarihi", "reviews_365", "inceleme_omur", "tabaka"]]
    s.to_csv(yol, index=False)
    return s


def cek(appid: int, hiz: Hiz) -> dict:
    sayfa, imlec, gorulen, n_istek = [], "*", set(), 0
    while True:
        hiz.bekle()
        j = http_json(f"https://store.steampowered.com/appreviews/{appid}",
                      {"json": 1, "filter": "recent", "language": "all", "purchase_type": "all", "review_type": "all", "num_per_page": 100, "cursor": imlec})  # fmt: skip
        n_istek += 1
        r = (j or {}).get("reviews") or []
        sayfa += [{k: x.get(k) for k in ALANLAR} | {"oynama_dk": (x.get("author") or {}).get("playtime_at_review")} for x in r]
        yeni = (j or {}).get("cursor")
        if not r or not yeni or yeni in gorulen:  # Steam imleci bazen tekrar ediyor → sonsuz döngü önlemi
            break
        gorulen.add(yeni)
        imlec = yeni
    return {"appid": appid, "incelemeler": sayfa, "istek": n_istek, "_fetched_at": simdi_utc()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paralel", type=int, default=3)
    ap.add_argument("--sinir", type=int, default=0, help=">0 ise yalnız ilk N oyun (deneme)")
    a = ap.parse_args()
    s = orneklem()
    yapilan = {x["appid"] for x in jsonl_gz_oku(CIKTI)}
    kalan = [int(i) for i in s.appid if int(i) not in yapilan]
    if a.sinir:
        kalan = kalan[: a.sinir]
    print(f"[m8] örneklem {len(s)} · kalan {len(kalan)} · tahmini inceleme {int(s[~s.appid.isin(yapilan)].inceleme_omur.sum()):,}", flush=True)
    sn = ayarlar()["hiz_limiti_saniye"]["inceleme"]
    with cf.ThreadPoolExecutor(a.paralel) as ex:
        isler = {ex.submit(cek, i, Hiz(sn)): i for i in kalan}
        for k, f in enumerate(cf.as_completed(isler), 1):
            r = f.result()
            jsonl_gz_ekle(CIKTI, [r])
            print(f"  {k}/{len(kalan)} appid={r['appid']} inceleme={len(r['incelemeler']):,} istek={r['istek']}", flush=True)
    print("[ok]")


if __name__ == "__main__":
    main()
