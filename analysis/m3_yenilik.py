"""M3 · Yenilik: "tanıdık ama farklı" mı kazanıyor? Doğrulayıcı: H1 (ters U).

Kullanım: python analysis/m3_yenilik.py
H1 (HIPOTEZLER): log(1+reviews_365) ~ nov + nov² + standart kontroller (+ log içerik etiket sayısı, R4). Destek: β₂ < 0, Lind–Mehlum
    U testi anlamlı (eğim x_L'de > 0, x_H'de < 0; x_L/x_H = 5./95. yüzdelik), dönüm noktası [x_L, x_H] içinde. Çürütme: β₂ anlamsız,
    ilişki monoton ya da dönüm noktası dışarıda. Ölçü = etiket kombinasyonu yeniliği (HIPOTEZLER değişiklik günlüğü 2026-10-24).
Duyarlılık: k=5/20, spline, hit (lojistik), R4 alt grubu (ömür boyu 10–50 inceleme).
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle
from ortak_model import KONTROL, hazirla, logit, ols
from scipy import stats

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Yenilik = etiket kombinasyonunun çıkıştan önceki en yakın 10 oyuna uzaklığı."
EK = " + log_etiket"  # R4: az etiketli oyunda yenilik ölçümü gürültülü


def lind_mehlum(m, x: str, x2: str, xl: float, xh: float) -> dict:
    b1, b2 = m.params[x], m.params[x2]
    V = m.cov_params().loc[[x, x2], [x, x2]].values
    sonuc = {}
    for ad, u in (("alt", xl), ("ust", xh)):
        g = np.array([1, 2 * u])
        egim, se = b1 + 2 * b2 * u, float(np.sqrt(g @ V @ g))
        sonuc[ad] = {"egim": float(egim), "t": float(egim / se)}
    p_alt = 1 - stats.norm.cdf(sonuc["alt"]["t"])  # H0: eğim(xL) ≤ 0
    p_ust = stats.norm.cdf(sonuc["ust"]["t"])  # H0: eğim(xH) ≥ 0
    tp = -b1 / (2 * b2)
    grad = np.array([-1 / (2 * b2), b1 / (2 * b2**2)])
    tp_se = float(np.sqrt(grad @ V @ grad))
    return {"b1": float(b1), "b2": float(b2), "p_b2": float(m.pvalues[x2]), "egimler": sonuc, "p_LM": float(max(p_alt, p_ust)),
            "donum": float(tp), "donum_alt": float(tp - 1.96 * tp_se), "donum_ust": float(tp + 1.96 * tp_se), "xL": xl, "xH": xh}  # fmt: skip


def karar(lm: dict) -> str:
    ok = lm["b2"] < 0 and lm["p_LM"] < 0.05 and lm["xL"] <= lm["donum"] <= lm["xH"]
    return "desteklendi" if ok else "desteklenmedi"


def model(d: pd.DataFrame, nov: str, sonuc: str = "y_log", tur: str = "ols"):
    d = d.assign(x=d[nov], x2=d[nov] ** 2)
    f = f"{sonuc} ~ x + x2 + {KONTROL}{EK}"
    return (ols if tur == "ols" else logit)(f, d), d


def main() -> None:
    stil()
    d = hazirla(orneklem(yukle()))
    d = d[d.novelty_k10.notna()].copy()
    d["log_etiket"] = np.log(d.n_icerik_etiket)
    xl, xh = d.novelty_k10.quantile([0.05, 0.95])
    m, dm = model(d, "novelty_k10")
    ana = lind_mehlum(m, "x", "x2", xl, xh)
    ana["karar"] = karar(ana)
    duy = {}
    for nov in ("novelty_k5", "novelty_k20"):
        dd = d[d[nov].notna()]
        a, b = dd[nov].quantile([0.05, 0.95])
        duy[nov] = lind_mehlum(model(dd, nov)[0], "x", "x2", a, b) | {"n": int(dd.shape[0])}
    duy["hit_lojistik"] = lind_mehlum(model(d, "novelty_k10", "y_hit", "logit")[0], "x", "x2", xl, xh)
    r4 = d[d.inceleme_omur.between(10, 50)]
    duy["R4_az_oylanmis"] = lind_mehlum(model(r4, "novelty_k10")[0], "x", "x2", *r4.novelty_k10.quantile([0.05, 0.95])) | {"n": len(r4)}
    for v in duy.values():
        v["karar"] = karar(v)

    # Grafik: tipik oyun için beklenen ilk yıl incelemesi (kuadratik + spline), ham ondalık dilimler
    ref = dm.iloc[[0]].copy()
    for c in ("yil", "fiyat"):
        ref[c] = dm[c].mode()[0]
    for c in ("ea", "log_dil", "log_etiket", "Action", "Adventure", "Casual", "RPG", "Simulation", "Strategy", "Sports", "Racing"):
        ref[c] = dm[c].median()
    izgara = np.linspace(d.novelty_k10.quantile(0.01), d.novelty_k10.quantile(0.99), 80)
    g = pd.concat([ref] * len(izgara), ignore_index=True).assign(x=izgara, x2=izgara**2)
    tah = m.get_prediction(g).summary_frame()
    beklenen = np.expm1(tah["mean"])
    sp = ols(f"y_log ~ bs(nov, df=5) + {KONTROL}{EK}", dm.assign(nov=dm.novelty_k10))
    sp_tah = np.expm1(sp.predict(g.assign(nov=izgara)))
    d["dilim"] = pd.qcut(d.novelty_k10, 10, labels=False)
    ham = d.groupby("dilim").agg(nov=("novelty_k10", "median"), medyan=("reviews_365", "median"), hit=("y_hit", "mean"))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(izgara, np.expm1(tah.mean_ci_lower), np.expm1(tah.mean_ci_upper), color=KATEGORIK[0], alpha=0.15, linewidth=0)
    ax.plot(izgara, beklenen, color=KATEGORIK[0], label="Kuadratik model (ön kayıtlı test)")
    ax.plot(izgara, sp_tah, color=KATEGORIK[1], linewidth=1.5, label="Esnek eğri (spline, duyarlılık)")
    if ana["xL"] <= ana["donum"] <= ana["xH"]:
        ax.axvline(ana["donum"], color=SOLUK, linewidth=1)
        ax.text(ana["donum"], ax.get_ylim()[1] * 0.97, f" dönüm noktası {ana['donum']:.2f}", fontsize=8.5, color=IKINCIL, va="top")
    for v in (xl, xh):
        ax.axvline(v, color="#c3c2b7", linewidth=1)
    ax.axvspan(izgara[0], xl, color="#f0efec", zorder=0)
    ax.text(izgara[0] + 0.003, ax.get_ylim()[0] + 0.15, "test penceresi\ndışı (az veri)", fontsize=8, color=IKINCIL, va="bottom")
    tepe = izgara[np.argmax(sp_tah.values)]
    if tepe < xl:
        ax.annotate("spline tepesi pencerenin dışında:\nbirebir kopya etiketler de iyi yapmıyor", (tepe, sp_tah.max()), xytext=(0.2, sp_tah.max() * 1.02),
                    fontsize=8.5, color=IKINCIL, arrowprops={"arrowstyle": "-", "color": SOLUK, "linewidth": 0.8})  # fmt: skip
    ax.set_xlabel("Yenilik skoru (0 = önceki oyunlarla aynı etiketler, yüksek = daha farklı)")
    ax.set_ylabel("Tipik bir oyun için beklenen ilk yıl inceleme")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.8)
    sonuc_metni = "DESTEKLENDİ" if ana["karar"] == "desteklendi" else "DESTEKLENMEDİ"
    baslik(fig, f"H1 {sonuc_metni}: " + ("en iyi sonuç orta düzeyde yenilikte" if ana["karar"] == "desteklendi" else "ters U yok; etiketler alışılmadıkça beklenen inceleme azalıyor"),
           f"Diğer her şey sabit, tipik oyun. Lind–Mehlum p={ana['p_LM']:.2g}; β₂={ana['b2']:.2f} (p={ana['p_b2']:.2g}). Gri dikeyler: 5. ve 95. yüzdelik.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M3_1_H1_yenilik", pd.DataFrame({"yenilik": izgara, "kuadratik": beklenen, "alt": np.expm1(tah.mean_ci_lower), "ust": np.expm1(tah.mean_ci_upper), "spline": sp_tah}).round(3), KAYNAK)  # fmt: skip

    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.plot(ham.nov, ham.hit * 100, color=KATEGORIK[0], marker="o", markersize=7)
    for i in (0, len(ham) - 1):
        ax.annotate(
            f"%{ham.hit.iloc[i] * 100:.1f}",
            (ham.nov.iloc[i], ham.hit.iloc[i] * 100),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=MUREKKEP,
        )
    ax.set_ylim(0, ham.hit.max() * 130)
    ax.set_xlabel("Yenilik skoru (her nokta oyunların %10'u)")
    ax.set_ylabel("Hit oranı (%)")
    baslik(fig, "Ham tablo: yenilik arttıkça hit oranı nasıl değişiyor?",
           "Kontrolsüz ham oranlar; tür, fiyat ve yıl farkları karışık. Ön kayıtlı test bir önceki grafikte.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M3_2_yenilik_ham", ham.round(4), KAYNAK)

    ozet = {"n": int(m.nobs), "H1": ana, "duyarlilik": duy, "ham": ham.round(4).to_dict()}
    (KOK / "analysis" / "sonuclar" / "M3_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "n": ozet["n"],
                "H1": ana,
                "duyarlilik_karar": {k: (v["karar"], round(v["b2"], 3), round(v["p_LM"], 4), round(v["donum"], 3)) for k, v in duy.items()},
            },
            ensure_ascii=False,
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
