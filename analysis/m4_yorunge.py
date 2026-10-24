"""M4 · Yörüngeler: inceleme eğrileri hangi tiplere ayrılıyor? Doğrulayıcı: H4 (Early Access → daha uzun kuyruk).

Kullanım: python analysis/m4_yorunge.py
H4 (HIPOTEZLER + 2026-10-24 ayrıntısı): tail_share ~ ea + kontroller (ea hariç), kesirli lojistik (GLM Binomial, logit bağ, HC1);
    yalnız reviews_365 ≥ 50; eşleştirilmiş tekrar (tür × fiyat birebir + PS). Destek: EA katsayısı > 0 ve anlamlı.
Yörüngeler (keşifsel): 24 aylık inceleme profili (her ay / 24 ay toplamı), k-means; k siluet skoruyla 3–6 arasından.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from grafik import KATEGORIK, KOK, MUREKKEP, SOLUK, YUZEY, baslik, kaydet, orneklem, stil, yukle
from m2_icerik import psm
from ortak_model import KONTROL, hazirla, katsayi
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

KAYNAK = "Kaynak: Steam inceleme grafiği; Discovery Dynamics analizi."
KONTROL_EA_SIZ = KONTROL.replace(" + ea", "")
GUN = np.timedelta64(1, "D")
AY = 365.25 / 12


def aylik_profil(appids: pd.Index, t0: pd.Series, n_ay: int = 24) -> pd.DataFrame:
    seri = pd.read_parquet(KOK / "data" / "interim" / "inceleme_seri.parquet")
    seri = seri[seri.appid.isin(appids)].copy()
    for c in ("bas", "son"):
        seri[c] = seri[c].astype("datetime64[ns]")
    t = seri.appid.map(t0).values.astype("datetime64[ns]")
    bas = np.maximum(seri.bas.values, t)
    son = seri.son.values
    uzun = (son - bas) / GUN
    toplam = seri.up.values + seri.down.values
    sutun = {}
    for i in range(n_ay):
        a, b = t + np.timedelta64(int(i * AY * 86400), "s"), t + np.timedelta64(int((i + 1) * AY * 86400), "s")
        ortak = np.clip((np.minimum(son, b) - np.maximum(bas, a)) / GUN, 0, None)
        pay = np.where((uzun > 0) & (son > t), ortak / np.where(uzun > 0, uzun, 1), 0.0)
        sutun[i + 1] = pd.Series(toplam * pay).groupby(seri.appid.values).sum()
    return pd.DataFrame(sutun).reindex(appids).fillna(0)


def h4(d: pd.DataFrame) -> dict:
    x = d[d.reviews_365 >= 50].copy()
    m = smf.glm(f"tail_share ~ ea + {KONTROL_EA_SIZ}", data=x, family=sm.families.Binomial()).fit(cov_type="HC1")
    k = katsayi(m, "ea", us=True)
    p = psm(x.reset_index(drop=True).assign(ea_t=lambda z: z.ea), "ea_t", "tail_share", kontrol=KONTROL_EA_SIZ, haric=("ea",))
    ham = x.groupby("ea").tail_share.median()
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for i, e in enumerate([0, 1]):
        v = x.loc[x.ea == e, "tail_share"] * 100
        parca = ax.violinplot(v, positions=[i], widths=0.7, showextrema=False, orientation="horizontal")
        for b in parca["bodies"]:
            b.set_facecolor(KATEGORIK[i])
            b.set_alpha(0.35)
        ax.scatter(v.median(), i, color=KATEGORIK[i], s=60, zorder=3, edgecolor=YUZEY, linewidth=1.5)
        ax.text(v.median(), i + 0.38, f"ortanca %{v.median():.0f}  (n={len(v):,})", ha="center", fontsize=9, color=MUREKKEP)
    ax.set_yticks([0, 1], ["Doğrudan tam sürüm", "Early Access ile çıkış"])
    ax.set_xlabel("İlk yılın incelemelerinden 90. günden SONRA gelenlerin payı (%)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 100)
    sonuc = "DESTEKLENDİ" if (k["tahmin"] > 1 and k["p"] < 0.05) else "DESTEKLENMEDİ"
    baslik(fig, f"H4 {sonuc}: Early Access oyunlarının ilgisi zamana daha yayılmış" if sonuc == "DESTEKLENDİ" else f"H4 {sonuc}: Early Access kuyruğu uzatmıyor",
           f"İlk yılında 50+ inceleme alan bağımsız oyunlar. Model (kontrollü): OR {k['tahmin']:.2f} (%95 GA {k['alt']:.2f}–{k['ust']:.2f}); "
           f"eşleştirilmiş fark {p['ATT'] * 100:+.1f} puan (maks SMD {p['maks_SMD']:.3f}).")  # fmt: skip
    fig.subplots_adjust(top=0.8, left=0.22)
    kaydet(fig, "M4_1_H4_early_access", ham.round(4).to_frame("ortanca_tail_share"), KAYNAK)
    return {"n": int(m.nobs), "OR": k, "psm": {kk: v for kk, v in p.items() if kk != "SMD"}, "ham_ortanca": ham.round(4).to_dict()}


def yorungeler(d: pd.DataFrame) -> dict:
    x = d[(d.reviews_365 >= 50) & d.reviews_2yil.notna()].copy()
    prof = aylik_profil(pd.Index(x.appid), x.set_index("appid").cikis)
    pay = prof.div(prof.sum(axis=1), axis=0)
    X = np.sqrt(pay.values)  # Hellinger: küçük payları da ayırt eder, ilk ay baskınlığını yumuşatır
    rng = np.random.default_rng(20261024)
    ornek = rng.choice(len(X), min(6000, len(X)), replace=False)
    skor = {k: silhouette_score(X[ornek], KMeans(k, n_init=10, random_state=0).fit(X).labels_[ornek]) for k in range(3, 7)}
    kbest = max(skor, key=skor.get)
    km = KMeans(kbest, n_init=20, random_state=0).fit(X)
    x["kume"] = km.labels_
    orta = pay.groupby(km.labels_).median()
    ilk3 = orta[[1, 2, 3]].sum(axis=1)
    ikinci_yil = orta[list(range(13, 25))].sum(axis=1)
    sira = ilk3.sort_values(ascending=False).index
    ad = {}
    for i, c in enumerate(sira):
        if i == 0:
            ad[c] = "Patlayıp sönen"
        elif ikinci_yil[c] == ikinci_yil.max():
            ad[c] = "Uzun soluklu"
        else:
            ad[c] = ["Hızlı başlangıç", "Dengeli", "Yavaş yanan", "Geç açılan"][min(i - 1, 3)]
    ozet = x.groupby("kume").agg(oyun=("appid", "size"), ea=("ea", "mean"), sevilen=("basari_sinifi", lambda v: (v == "sevilen_hit").mean()),
                                  hit=("y_hit", "mean"), medyan_r365=("reviews_365", "median"))  # fmt: skip
    ozet["pay"] = ozet.oyun / ozet.oyun.sum() * 100
    ozet["ad"] = ozet.index.map(ad)
    ozet["ilk3_ay"] = ilk3 * 100
    ozet["ikinci_yil"] = ikinci_yil * 100

    fig, eksen = plt.subplots(1, kbest, figsize=(3.2 * kbest, 4.6), sharey=True)
    for ax, c in zip(np.atleast_1d(eksen), sira):
        for j in rng.choice(np.where(km.labels_ == c)[0], 40, replace=False):
            ax.plot(range(1, 25), pay.iloc[j] * 100, color=SOLUK, alpha=0.12, linewidth=0.8)
        ax.plot(range(1, 25), orta.loc[c] * 100, color=KATEGORIK[0], linewidth=2.5)
        r = ozet.loc[c]
        ax.set_title(f"{r.ad}\n%{r.pay:.0f} oyun · EA %{r.ea * 100:.0f} · hit %{r.hit * 100:.0f}", fontsize=9.5)
        ax.set_xticks([1, 6, 12, 18, 24])
        ax.axvline(12.5, color="#e1e0d9", linewidth=1)
        ax.set_xlabel("Çıkıştan sonraki ay")
    np.atleast_1d(eksen)[0].set_ylabel("O ayın 2 yıllık incelemedeki payı (%)")
    uzun, patlayan = ozet.loc[ozet.ad == "Uzun soluklu"].iloc[0], ozet.loc[ozet.ad == "Patlayıp sönen"].iloc[0]
    baslik(fig, f"KEŞİFSEL: İlgisi uzun süren oyunların hit oranı, patlayıp sönenlerin {uzun.hit / patlayan.hit:.0f} katı",
           f"İlk yılında 50+ inceleme alan, 2 yılı gözlenmiş {len(x):,} bağımsız oyun; k-means {kbest} tip. Siluet {skor[kbest]:.2f} düşük: tipler ayrık değil, bir sürekliliğin kaba özeti.\n"
           "Mavi = tipin ortanca eğrisi; gri = örnek oyunlar; dikey çizgi = 1. yıl sonu.")  # fmt: skip
    fig.subplots_adjust(top=0.68, bottom=0.2, wspace=0.12)
    kaydet(fig, "M4_2_yorunge_tipleri", ozet.round(4), KAYNAK + f" k-means, k={kbest} (siluet {skor[kbest]:.3f}).")
    return {"n": len(x), "k": kbest, "siluet": {k: round(v, 4) for k, v in skor.items()}, "kumeler": ozet.round(4).to_dict("index")}


def main() -> None:
    stil()
    d = hazirla(orneklem(yukle()))
    ozet = {"H4": h4(d), "yorunge": yorungeler(d)}
    (KOK / "analysis" / "sonuclar" / "M4_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
