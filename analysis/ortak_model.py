"""Ortak model yardımcıları. Ön kayıttaki standart kontroller (HIPOTEZLER "Ortak kurallar") tek yerde tanımlı.

Standart kontroller: çıkış yılı (sabit etki) · ana tür (Steam geliştirici türleri, 8 kukla) · fiyat bandı (F2P dahil kategori) ·
Early Access ile çıkış · dil sayısı (log). Birincil sonuç log(1 + reviews_365); ikili sonuç hit. Standart hata HC1 (değişen varyansa dayanıklı).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import KOK

TURLER = ["Action", "Adventure", "Casual", "RPG", "Simulation", "Strategy", "Sports", "Racing"]
KONTROL = "C(yil) + " + " + ".join(TURLER) + " + C(fiyat, Treatment('5-10')) + ea + log_dil"


def hazirla(a: pd.DataFrame) -> pd.DataFrame:
    """Model değişkenlerini ekler; fiyatı bilinmeyen (ücretli ama satın alınamayan) oyunları çıkarır."""
    tr = pd.read_parquet(KOK / "data" / "interim" / "oyun_steam_tur.parquet")
    tr = tr[tr.tur.isin(TURLER)]
    kukla = pd.crosstab(tr.appid, tr.tur).clip(upper=1).reindex(columns=TURLER, fill_value=0)
    d = a.merge(kukla, left_on="appid", right_index=True, how="left").fillna({t: 0 for t in TURLER})
    d = d[d.fiyat_bandi.notna()].copy()
    d["fiyat"] = d.fiyat_bandi.astype(str)
    d["ea"] = d.ea_ile_basladi.astype(int)
    d["log_dil"] = np.log1p(d.n_dil)
    d["y_log"] = np.log1p(d.reviews_365)
    d["y_hit"] = d.hit.astype(int)
    d["deneyimli"] = (d.gelistirici_onceki_oyun >= 1).astype(int)
    d["kendi"] = d.kendi_yayini.eq(True).astype(int)
    return d


def ols(formul: str, d: pd.DataFrame):
    return smf.ols(formul, data=d).fit(cov_type="HC1")


def logit(formul: str, d: pd.DataFrame):
    return smf.logit(formul, data=d).fit(disp=0, cov_type="HC1")


def katsayi(m, terim: str, us: bool = False) -> dict:
    """Tek terimin tahmini, %95 GA ve p. us=True → exp (lojistikte olasılık oranı, log-OLS'de yüzde değişim çarpanı)."""
    b, (lo, hi), p = m.params[terim], m.conf_int().loc[terim], m.pvalues[terim]
    f = np.exp if us else (lambda x: x)
    return {"tahmin": float(f(b)), "alt": float(f(lo)), "ust": float(f(hi)), "p": float(p), "n": int(m.nobs)}


def holm(p: dict[str, float]) -> dict[str, float]:
    """Holm–Bonferroni düzeltilmiş p değerleri."""
    s = sorted(p.items(), key=lambda kv: kv[1])
    m, out, onceki = len(s), {}, 0.0
    for i, (k, v) in enumerate(s):
        onceki = max(onceki, min(1.0, (m - i) * v))
        out[k] = onceki
    return out


def beklenen_hit(d: pd.DataFrame) -> pd.Series:
    """Standart kontrollerle (KONTROL) hit olasılığı. K5/K6'da "gözlenen ÷ beklenen" için: bir grubun hit oranı yalnız
    fiyat, tür, yıl, EA ve dil karışımından beklenenden yüksek mi? d = hazirla() çıktısı (F2P dahil, fiyat kategorisi)."""
    m = logit(f"y_hit ~ {KONTROL}", d)
    return pd.Series(m.predict(d), index=d.index)


def gozlenen_beklenen(gozlenen: int, beklenen: float) -> dict:
    """O/B oranı ve %95 GA (gözlenen sayı Poisson; beklenen sabit kabul edilir, büyük örneklem modelinden geldiği için)."""
    from scipy import stats

    alt = stats.chi2.ppf(0.025, 2 * gozlenen) / 2 if gozlenen > 0 else 0.0
    ust = stats.chi2.ppf(0.975, 2 * (gozlenen + 1)) / 2
    return {"gozlenen": int(gozlenen), "beklenen": float(beklenen), "ob": gozlenen / beklenen, "alt": alt / beklenen, "ust": ust / beklenen}
