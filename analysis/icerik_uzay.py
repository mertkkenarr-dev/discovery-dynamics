"""İçerik uzayı: 11c'deki vektörlerin AYNISI (ilk 10 içerik etiketi, sıra × 2018 öncesi IDF, L2 normalize).
Galaksi haritası, yenilik (M3) ve K5/K6 aynı uzayı kullanır; tanım tek yerde (scripts/11c_icerik.vektorler) kalsın diye buradan çağrılır.
"""

from __future__ import annotations

import importlib
import sys

import numpy as np
import pandas as pd
from grafik import KOK

sys.path.insert(0, str(KOK / "scripts"))
_11c = importlib.import_module("11c_icerik")
_ortak = importlib.import_module("ortak")


def yukle_uzay(t: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """t: oyun_tablosu. Dönen: çıkışa göre sıralı, ≥ min_etiket içerik etiketli oyunlar ve satır satır hizalı vektörleri.
    IDF tüm oyunlarla (11c ile aynı girdi) hesaplanır; filtre vektörden sonra uygulanır."""
    cfg = _ortak.ayarlar()
    o = t[t.cikis.notna()].sort_values("cikis", kind="stable").reset_index(drop=True)
    X, n_et = _11c.vektorler(o[["appid", "cikis"]], cfg)
    tut = n_et >= cfg["icerik"]["min_etiket"]
    return o[tut].reset_index(drop=True), X[tut]


def etiket_adlari(t: pd.DataFrame, n_sutun: int) -> np.ndarray:
    """Vektör sütun sırasıyla etiket adları. 11c sütunları, girdideki oyunların ilk N içerik etiketinde geçen tagid'lerin sıralı
    listesidir; aynı süzme burada tekrarlanır ve sütun sayısı tutmazsa hata verir (sessiz kayma olmasın)."""
    cfg = _ortak.ayarlar()
    c = cfg["icerik"]
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    icerik = set(tx.tagid[tx.boyut.isin(c["icerik_boyutlari"])])
    o = t[t.cikis.notna()]
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "tagid", "sira", "ad"])
    e = e[e.tagid.isin(icerik) & e.appid.isin(o.appid)].sort_values(["appid", "sira"])
    e = e[e.groupby("appid").cumcount() + 1 <= c["ilk_n_etiket"]]
    ad = e.drop_duplicates("tagid").set_index("tagid").ad.sort_index()
    if len(ad) != n_sutun:
        raise ValueError(f"Etiket sütunları tutmuyor: {len(ad)} ad, {n_sutun} sütun")
    return ad.values
