"""Duyarlılık: etiket kapsamı 2021 öncesi seçilimli (KESIFSEL günlüğü, 2026-10-25). Etiket tabanlı bulgular 2021–2025 çıkışlı
oyunlarla yeniden hesaplanır ve tam örneklemle yan yana konur. Hipotez kararları DEĞİŞMEZ (ön kayıt tam örneklemle); bu bir sağlamlık kontrolü.

Kullanım: cd analysis && python duyarlilik_2021.py
Kapsam: M3/H1 (yenilik), M2/H7 (doygunluk), M2 çok oyunculu etiketler, K5 (takipçi / öncül / plasebo hit oranı), K6 (fırsat bölgeleri O/B).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from grafik import KOK, orneklem, yukle
from icerik_uzay import yukle_uzay
from k5_klon import ESIK, basari, oncu_ve_plasebo, takipciler
from m3_yenilik import karar, lind_mehlum, model
from ortak_model import KONTROL, beklenen_hit, gozlenen_beklenen, hazirla, katsayi, logit

YIL_MIN = 2021


def kapsam(d: pd.DataFrame) -> dict:
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "sira"])
    n = e[e.sira <= 20].groupby("appid").size()
    x = d.assign(n_etiket=d.appid.map(n).fillna(0))
    return {int(y): {"etiketsiz_yuzde": float((g.n_etiket == 0).mean() * 100), "hit_etiket": float(g[g.y_hit == 1].n_etiket.mean()),
                     "diger_etiket": float(g[g.y_hit == 0].n_etiket.mean())} for y, g in x.groupby("yil")}  # fmt: skip


def h1(d: pd.DataFrame) -> dict:
    d = d[d.novelty_k10.notna()].copy()
    d["log_etiket"] = np.log(d.n_icerik_etiket)
    xl, xh = d.novelty_k10.quantile([0.05, 0.95])
    lm = lind_mehlum(model(d, "novelty_k10")[0], "x", "x2", xl, xh)
    return {"n": len(d), "b2": lm["b2"], "p_b2": lm["p_b2"], "egim_alt_t": lm["egimler"]["alt"]["t"], "egim_ust_t": lm["egimler"]["ust"]["t"], "karar": karar(lm)}


def h7(d: pd.DataFrame) -> dict:
    d = d[d.kombo_12ay.notna()].copy()
    d["log_doy"] = np.log1p(d.kombo_12ay.astype(float))
    return katsayi(logit(f"y_hit ~ log_doy + C(ana_tur) + {KONTROL}", d), "log_doy", us=True)


def cok_oyunculu(d: pd.DataFrame) -> dict:
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "sira", "ad"])
    e = e[e.sira <= 10]
    sat = {}
    for ad in ("Multiplayer", "Online Co-Op", "Co-op"):
        x = d.assign(var=d.appid.isin(e.appid[e.ad == ad]).astype(int))
        sat[ad] = katsayi(logit(f"y_hit ~ var + {KONTROL}", x), "var", us=True)
    return sat


def k5(t: pd.DataFrame, a: pd.DataFrame) -> dict:
    u, X = yukle_uzay(t)
    temiz = ~(u.yetiskin | u.seri_uretici | u.yazilim_suphe | u.listelenmemis).values
    u, X = u[temiz].reset_index(drop=True), X[temiz]
    oncu, plasebo = oncu_ve_plasebo(u)
    plasebo = plasebo[plasebo >= 0]
    out = {}
    for ad, aa in (("tam", a), ("2021+", a[a.yil >= YIL_MIN])):
        aa = aa.assign(p_hit=beklenen_hit(aa))
        out[ad] = {k: basari(aa, takipciler(u, X, m, ESIK, yon), u).attrs["tum"] for k, m, yon in (("takipci", oncu, 1), ("oncul", oncu, -1), ("plasebo", plasebo, 1))}
    return out


def k6(a: pd.DataFrame) -> dict:
    b = pd.read_parquet(KOK / "data" / "interim" / "k6_bolge.parquet")
    oz = json.loads((KOK / "analysis" / "sonuclar" / "K6_ozet.json").read_text(encoding="utf-8"))
    firsat = {r["bolge"]: r["ad"] for r in oz["bolgeler"] if r["firsat"]}
    out = {}
    for ad, aa in (("tam", a), ("2021+", a[a.yil >= YIL_MIN].copy())):
        aa = aa.assign(p_hit=beklenen_hit(aa)).merge(b, on="appid")
        out[ad] = {firsat[k]: gozlenen_beklenen(int(g.y_hit.sum()), float(g.p_hit.sum())) | {"n": len(g)} for k, g in aa.groupby("bolge") if k in firsat}
    return out


def main() -> None:
    t = yukle()
    d = hazirla(orneklem(t))
    d21 = d[d.yil >= YIL_MIN]
    sonuc = {
        "kapsam": kapsam(d),
        "H1": {"tam": h1(d), "2021+": h1(d21)},
        "H7": {"tam": h7(d), "2021+": h7(d21)},
        "cok_oyunculu": {"tam": cok_oyunculu(d), "2021+": cok_oyunculu(d21)},
        "K6": k6(d),
        "K5": k5(t, d),
    }
    (KOK / "analysis" / "sonuclar" / "duyarlilik_2021.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for k in ("H1", "H7", "cok_oyunculu", "K6", "K5"):
        print(k, json.dumps(sonuc[k], ensure_ascii=False, default=float)[:900])


if __name__ == "__main__":
    main()
