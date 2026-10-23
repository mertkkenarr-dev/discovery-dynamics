"""11d: İkincil başarı ailesi — beğeni, ticari, kalıcılık, göreli sıra, başarı sınıfı. Tanımlar HIPOTEZLER.md (2026-10-24) ile birebir.

Kullanım: cd scripts && python 11d_basari.py        (11_sonuc ve 11b'den sonra)
Çıktı   : interim/basari.parquet
Pencere hesabı 11_sonuc.pencere ile aynı mantık, tüm seri üzerinde vektörel. Güvence: aynı kodla reviews_365 yeniden hesaplanır ve
11_sonuc'un değeriyle karşılaştırılır; uyuşmazsa betik durur (iki bağımsız uygulama aynı sayıyı vermeli).
Hipotez testi YOK.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from ortak import INTERIM, KOK, KararKaydi

GUN = np.timedelta64(1, "D")
SATIS_KATSAYI = (20, 30, 40)  # inceleme başına satış (Boxleiter aralığı; orta = 30)
TICARI_ESIK = 100_000  # brüt USD


def pencere_toplam(seri: pd.DataFrame, t0: pd.Series, a: int, b: int) -> tuple[pd.Series, pd.Series]:
    """[t0+a, t0+b) gün penceresine düşen olumlu/olumsuz, oyun başına. Kova t0'dan önce başlıyorsa t0'dan kırpılır (11_sonuc ile aynı)."""
    s = seri.assign(t0=seri.appid.map(t0)).dropna(subset=["t0"])
    bas = np.maximum(s.bas.values, s.t0.values)
    son = s.son.values
    uzun = (son - bas) / GUN
    ust = np.minimum(son, s.t0.values + b * GUN)
    alt = np.maximum(bas, s.t0.values + a * GUN)
    ortak = np.clip((ust - alt) / GUN, 0, None)
    pay = np.where((uzun > 0) & (son > s.t0.values), ortak / np.where(uzun > 0, uzun, 1), 0.0)
    return pd.Series(s.up.values * pay).groupby(s.appid.values).sum(), pd.Series(s.down.values * pay).groupby(s.appid.values).sum()


def wilson_alt(p: pd.Series, n: pd.Series, z: float = 1.96) -> pd.Series:
    alt = ((p + z**2 / (2 * n)) - z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / (1 + z**2 / n)
    return alt.clip(0, 1)  # p = 0'da kayan nokta −3e−17 üretiyor (12_kontrol yakaladı)


def main() -> None:
    K = KararKaydi("11d_basari")
    s = pd.read_parquet(INTERIM / "sonuc.parquet")
    f = pd.read_parquet(INTERIM / "oznitelik.parquet", columns=["appid", "fiyat_liste_usd", "f2p", "yil"])
    seri = pd.read_parquet(INTERIM / "inceleme_seri.parquet")
    for c in ("bas", "son"):
        seri[c] = seri[c].astype("datetime64[ns]")
    h = s[s.sonuc_kaynagi == "histogram"].set_index("appid")
    t0 = h.ilk_cikis.astype("datetime64[ns]")

    # Güvence: bağımsız vektörel uygulama, 11_sonuc ile aynı reviews_365'i vermeli
    up, dn = pencere_toplam(seri, t0, 0, 365)
    kontrol = (up + dn).reindex(h.index)
    dolu = h.reviews_365.notna()
    fark = (kontrol[dolu] - h.reviews_365[dolu]).abs()
    print(f"Güvence: vektörel reviews_365 vs 11_sonuc → en büyük fark {fark.max():.2e} (n={int(dolu.sum()):,})")
    if fark.max() > 1e-6:
        sys.exit("reviews_365 iki uygulamada uyuşmuyor; pencere mantığı ayrışmış.")

    # Kalıcılık: 366.–730. gün; 2. yıl sınır kovası tam gözlenmiş olmalı (R2)
    u2, d2 = pencere_toplam(seri, t0, 365, 730)
    son_kova = seri.groupby("appid").bas.max()
    tam = (t0 + np.timedelta64(730, "D")) <= son_kova.reindex(t0.index)
    r2 = (u2 + d2).reindex(h.index).where(tam)

    o = s[["appid", "kohort", "reviews_365", "olumlu_oran_365", "hit"]].merge(f, on="appid", how="left")
    o["reviews_2yil"] = o.appid.map(r2)
    o["kalicilik"] = (o.reviews_2yil / o.reviews_365).where(o.reviews_365 >= 50)
    o["begeni_wilson"] = wilson_alt(o.olumlu_oran_365, o.reviews_365).where(o.reviews_365 > 0)

    ucretli = ~o.f2p.fillna(False).astype(bool) & o.fiyat_liste_usd.notna()
    for ad, kat in zip(("alt", "orta", "ust"), SATIS_KATSAYI):
        o[f"brut_gelir_{ad}"] = (o.reviews_365 * kat * o.fiyat_liste_usd).where(ucretli)
    o["brut_gelir_alt"] = o.brut_gelir_alt.where(o.reviews_365 >= 50)
    o["brut_gelir_ust"] = o.brut_gelir_ust.where(o.reviews_365 >= 50)
    o["ticari_basari"] = (o.brut_gelir_orta >= TICARI_ESIK).astype("boolean").where(ucretli & o.reviews_365.notna())

    # Göreli: yıl × ana tür (oyunun en güçlü 'ana' tür etiketi) içinde yüzdelik
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    ana = set(tx.tagid[(tx.boyut == "A_tur") & (tx.alt_grup == "ana")])
    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet", columns=["appid", "tagid", "sira", "ad"])
    e = e[e.tagid.isin(ana)].sort_values(["appid", "sira"]).drop_duplicates("appid")
    o["ana_tur"] = o.appid.map(e.set_index("appid").ad).fillna("diger")
    ref = o.kohort & o.reviews_365.notna()
    o["goreli_yuzdelik"] = o[ref].groupby(["yil", "ana_tur"]).reviews_365.rank(pct=True).reindex(o.index)

    r = o.reviews_365.round()
    oo = o.olumlu_oran_365
    sinif = np.select(
        [r < 10, (r >= 500) & (oo >= 0.80), (r >= 500) & (oo >= 0.70), r >= 500, (r >= 50) & (o.begeni_wilson >= 0.85)],
        ["gorunmez", "sevilen_hit", "hit", "tartismali_hit", "sessiz_basari"],
        default="orta",
    )
    o["basari_sinifi"] = pd.Series(sinif, index=o.index).where(o.reviews_365.notna())
    k = o[o.kohort & o.reviews_365.notna()]
    print("\nBaşarı sınıfları (kohort, reviews_365 dolu):", (k.basari_sinifi.value_counts(normalize=True) * 100).round(1).to_dict())
    K.ekle(
        "B01",
        "2. yıl penceresi tam gözlenmemiş",
        int((o.kohort & o.reviews_365.ge(50) & o.reviews_2yil.isna()).sum()),
        int((o.kohort & o.reviews_365.ge(50)).sum()),
        "kalicilik = NULL",
        "R2: sağdan sansür",
    )
    K.ekle(
        "B02",
        "Ticari ölçü tanımsız (F2P ya da fiyat bilinmiyor)",
        int((o.kohort & o.reviews_365.notna() & ~ucretli).sum()),
        int(k.shape[0]),
        "brut_gelir ve ticari_basari = NULL",
        "Gelir formülü fiyat gerektirir; F2P geliri gözlenmez",
    )

    cikti = o[
        [
            "appid",
            "begeni_wilson",
            "reviews_2yil",
            "kalicilik",
            "brut_gelir_alt",
            "brut_gelir_orta",
            "brut_gelir_ust",
            "ticari_basari",
            "ana_tur",
            "goreli_yuzdelik",
            "basari_sinifi",
        ]
    ]
    cikti.to_parquet(INTERIM / "basari.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] basari: {len(cikti):,} oyun")


if __name__ == "__main__":
    main()
