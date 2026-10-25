"""K10 (keşifsel) · Türler: alt tür karnesi (risk-ödül), hibrit türler (parçalarından iyi mi), eğilimler.

Kullanım: cd analysis && python k10_tur.py
Tanımlar sonuçlara bakılmadan docs/KESIFSEL_K5_K8.md §K10'da sabitlendi. Grafikler k10_grafik.py'de.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from grafik import KOK, orneklem, wilson, yukle
from k10_grafik import ciz_egilim, ciz_hibrit, ciz_karne
from ortak_model import KONTROL, beklenen_hit, gozlenen_beklenen, hazirla, logit
from scipy import stats
from statsmodels.stats.multitest import multipletests

MIN_KARNE, MIN_MODEL, MIN_CIFT, JACCARD = 500, 100, 150, 0.5
# Etiket kapsamı 2021'den önce seçilimli: 2018–19'da oyunların ~%54'ünde alt tür etiketi var ve hit'ler iki kat fazla tür etiketi taşıyor;
# 2021'den itibaren kapsam ~%92 ve hit / hit olmayan etiket sayısı eşit (KESIFSEL günlüğü, 2026-10-25). Üyelik ancak 2021+ yansız.
YIL_MIN = 2021
UCRETLI = ["<5", "5-10", "10-20", "20-30", ">=30"]  # oyun_tablosu.fiyat_bandi değerleri


def uyelik(t: pd.DataFrame) -> pd.DataFrame:
    """appid × alt tür (0/1): alt tür etiketi oyunun ilk 10 etiketinde mi (sıra, oy değil; R4)."""
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    alt = set(tx.tagid[(tx.boyut == "A_tur") & (tx.alt_grup != "ana")])
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "tagid", "sira", "ad"])
    e = e[(e.sira <= 10) & e.tagid.isin(alt) & e.appid.isin(t.appid)]
    return pd.crosstab(e.appid, e.ad).clip(upper=1)


def newcombe(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float, float]:
    """p2 − p1 ve Newcombe (Wilson tabanlı) %95 GA, yüzde puan."""
    p1, p2 = k1 / n1, k2 / n2
    (l1, u1), (l2, u2) = [(float(x.iloc[0]), float(y.iloc[0])) for x, y in (wilson(pd.Series([k1]), pd.Series([n1])), wilson(pd.Series([k2]), pd.Series([n2])))]
    d = p2 - p1
    return d * 100, (d - np.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)) * 100, (d + np.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)) * 100


def karne(a: pd.DataFrame, U: pd.DataFrame, t: pd.DataFrame, Ut: pd.DataFrame) -> pd.DataFrame:
    turler = [c for c in U.columns if U[c].sum() >= MIN_KARNE]
    y = t.set_index("appid").cikis.dt.year
    yil_t = y.reindex(Ut.index)
    genel = ((yil_t >= 2024).sum()) / max((yil_t.isin([2022, 2023])).sum(), 1)
    sat = []
    for c in turler:
        x = a[a.appid.isin(U.index[U[c] == 1])]
        n, k, g0 = len(x), int(x.y_hit.sum()), int((x.kademe.astype(str) == "T0").sum())
        (hl, hu), (gl, gu) = [(float(p.iloc[0]) * 100, float(q.iloc[0]) * 100) for p, q in (wilson(pd.Series([k]), pd.Series([n])), wilson(pd.Series([g0]), pd.Series([n])))]
        ob = gozlenen_beklenen(k, float(x.p_hit.sum()))
        yt = yil_t[Ut[c] == 1]
        arz = int(yt.between(2022, 2025).sum())
        buyume = ((yt >= 2024).sum() / max(yt.isin([2022, 2023]).sum(), 1)) / genel
        fb = x[x.fiyat_bandi.isin(UCRETLI)].groupby("fiyat_bandi").y_hit.agg(["mean", "size"])
        fb = fb[fb["size"] >= 100]
        erken, gec = x[x.yil.between(2021, 2022)], x[x.yil.between(2023, 2024)]
        d, dl, du = newcombe(int(erken.y_hit.sum()), len(erken), int(gec.y_hit.sum()), len(gec)) if len(erken) and len(gec) else (np.nan,) * 3
        sat.append({"tur": c, "n": n, "hit": k / n * 100, "hit_alt": hl, "hit_ust": hu, "gorunmez": g0 / n * 100, "gorunmez_alt": gl, "gorunmez_ust": gu,
                    "ob": ob["ob"], "ob_alt": ob["alt"], "ob_ust": ob["ust"], "arz_22_25": arz, "goreli_buyume": float(buyume),
                    "tatli_fiyat": fb["mean"].idxmax() if len(fb) else None, "tatli_fiyat_hit": float(fb["mean"].max() * 100) if len(fb) else None,
                    "hit_erken": erken.y_hit.mean() * 100, "hit_gec": gec.y_hit.mean() * 100, "egilim": d, "egilim_alt": dl, "egilim_ust": du,
                    "ortanca_fiyat": float(x.fiyat_liste_usd.median())})  # fmt: skip
    return pd.DataFrame(sat).sort_values("hit", ascending=False).reset_index(drop=True)


def hibrit(a: pd.DataFrame, U: pd.DataFrame) -> pd.DataFrame:
    """Beklenen: kontroller + tüm (≥ MIN_MODEL) alt tür kuklalarının ana etkileri; O/B > 1 = karışım parçalarından iyi."""
    model_tur = [c for c in U.columns if U[c].sum() >= MIN_MODEL]
    D = U.reindex(a.appid).fillna(0)[model_tur].astype(int).values
    ad = [f"g{i}" for i in range(len(model_tur))]
    x = a.reset_index(drop=True).join(pd.DataFrame(D, columns=ad))
    m = logit(f"y_hit ~ {KONTROL} + " + " + ".join(ad), x)
    p = m.predict(x).values
    sat = []
    for i in range(len(model_tur)):
        for j in range(i + 1, len(model_tur)):
            ai, aj = model_tur[i].lower(), model_tur[j].lower()
            if ai in aj or aj in ai:
                continue
            ikisi = (D[:, i] == 1) & (D[:, j] == 1)
            n = int(ikisi.sum())
            if n < MIN_CIFT:
                continue
            jac = n / int(((D[:, i] == 1) | (D[:, j] == 1)).sum())
            if jac > JACCARD:
                continue
            o, e = int(x.y_hit.values[ikisi].sum()), float(p[ikisi].sum())
            pv = min(1.0, 2 * min(stats.poisson.cdf(o, e), stats.poisson.sf(o - 1, e)))
            sat.append({"cift": f"{model_tur[i]} + {model_tur[j]}", "a": model_tur[i], "b": model_tur[j], "n": n, "hit": o / n * 100, "jaccard": jac,
                        **{k: v for k, v in gozlenen_beklenen(o, e).items() if k in ("gozlenen", "beklenen", "ob", "alt", "ust")}, "p": pv})  # fmt: skip
    h = pd.DataFrame(sat)
    h["q"] = multipletests(h.p, method="fdr_bh")[1]
    return h.sort_values("ob", ascending=False).reset_index(drop=True)


def main() -> None:
    t = yukle()
    a = hazirla(orneklem(t))
    a = a[a.yil >= YIL_MIN].copy()
    a["p_hit"] = beklenen_hit(a)
    U = uyelik(a)
    Ut = uyelik(t[t.kohort])
    k = karne(a, U, t, Ut)
    h = hibrit(a, U)
    pd.set_option("display.width", 250)
    print(k[["tur", "n", "hit", "gorunmez", "ob", "arz_22_25", "goreli_buyume", "tatli_fiyat", "egilim"]].round(2).to_string())
    print(f"çift {len(h)}, q<0,05: {(h.q < 0.05).sum()}, p<0,05: {(h.p < 0.05).sum()}; O/B dağılımı", h.ob.describe().round(2).to_dict())
    print(h[h.q < 0.05][["cift", "n", "hit", "ob", "alt", "ust", "q"]].round(3).head(12).to_string())
    print(h[h.q < 0.05][["cift", "n", "hit", "ob", "alt", "ust", "q"]].round(3).tail(8).to_string())
    ciz_karne(k, float(a.y_hit.mean() * 100), float((a.kademe.astype(str) == "T0").mean() * 100))
    ciz_hibrit(h)
    ciz_egilim(k)
    Ut.stack().rename("uye").reset_index().query("uye == 1").drop(columns="uye").query("ad in @k.tur").to_parquet(
        KOK / "data" / "interim" / "k10_uyelik.parquet", index=False)  # fmt: skip
    ozet = {"orneklem_hit": float(a.y_hit.mean() * 100), "orneklem_gorunmez": float((a.kademe.astype(str) == "T0").mean() * 100),
            "karne": k.round(4).to_dict(orient="records"), "hibrit": h.round(5).to_dict(orient="records"), "n_cift": len(h),
            "n_anlamli": int((h.q < 0.05).sum())}  # fmt: skip
    (KOK / "analysis" / "sonuclar" / "K10_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
