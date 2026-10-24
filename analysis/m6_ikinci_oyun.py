"""M6 · Öğrenme eğrisi: stüdyolar ikinci oyunlarında daha mı başarılı? Doğrulayıcı: H5.

Kullanım: python analysis/m6_ikinci_oyun.py
Çift tanımı: geliştiricinin Steam'deki (tüm zamanlar) 1. ve 2. oyunu (studyo_oyun.sira 1 ve 2; aynı gün çıkan, sırası belirsiz olanlar dışarıda).
    Ana örneklem: iki oyun da analiz örnekleminde (kohort, organik, bayraksız, reviews_365 dolu). Duyarlılık: 2. oyunda organik şartı yok.
H5: Wilcoxon işaretli sıra (Δ log(1+reviews_365) > 0) + birinci farklar regresyonu (stüdyo sabit etkisine denk; kontroller: arada
    geçen yıl, Δtür, Δfiyat, Δdil, ΔEA). Seçilim/ortalamaya dönüş: ilk oyunun kademesine göre tabakalama.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import KADEME_AD, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle
from ortak_model import TURLER, hazirla
from scipy import stats

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. Stüdyo = geliştirici (sabit kimlik ya da normalize ad)."
FIYATLAR = ["f2p", "<5", "10-20", "20-30", ">=30"]  # 5-10 referans


def ciftler(t: pd.DataFrame, a: pd.DataFrame, organik_ikinci: bool = True, sadece_id: bool = False, sadece_hist: bool = False) -> pd.DataFrame:
    so = pd.read_parquet(KOK / "data" / "interim" / "studyo_oyun.parquet")
    say = so.groupby(["studyo_anahtar", "sira"]).appid.transform("size")
    so = so[(so.sira <= 2) & (say == 1)]  # aynı gün çıkan (sıra eşit) oyunlar belirsiz → dışarıda
    if sadece_id:  # ad eşlemesi farklı stüdyoları birleştirebilir → yalnız Steam sabit kimliği
        so = so[so.studyo_anahtar.str.startswith("id:")]
    p = so.pivot(index="studyo_anahtar", columns="sira", values="appid").dropna().astype(int)
    p.columns = ["ilk", "ikinci"]
    havuz2 = a if organik_ikinci else hazirla(t[t.kohort & t.reviews_365.notna() & ~t.seri_uretici & ~t.yetiskin & ~t.yazilim_suphe & ~t.listelenmemis])
    a1 = a.set_index("appid")
    a2 = havuz2.set_index("appid")
    p = p[p.ilk.isin(a1.index) & p.ikinci.isin(a2.index)]
    p = p[~p.ikinci.duplicated(keep=False) & ~p.ilk.duplicated(keep=False)]  # ortak geliştirilen oyun iki çiftte sayılmasın
    s = ["y_log", "kademe", "yil", "cikis", "fiyat", "log_dil", "ea", "basari_sinifi", "ana_tur", "sonuc_kaynagi", *TURLER]
    x = p.join(a1.loc[p.ilk, s].set_axis(p.index).add_suffix("_1")).join(a2.loc[p.ikinci, s].set_axis(p.index).add_suffix("_2"))
    if sadece_hist:  # < 10 incelemede reviews_365 = ömür boyu üst sınır; eski ilk oyun daha çok biriktirmiş olabilir
        x = x[(x.sonuc_kaynagi_1 == "histogram") & (x.sonuc_kaynagi_2 == "histogram")]
    x["delta"] = x.y_log_2 - x.y_log_1
    x["ara_yil"] = (x.cikis_2 - x.cikis_1).dt.days / 365.25
    for c in ["log_dil", "ea", *TURLER]:
        x[f"d_{c}"] = x[f"{c}_2"] - x[f"{c}_1"]
    for f in FIYATLAR:
        x[f"d_f_{f.replace('<', 'lt').replace('>=', 'ge').replace('-', '_')}"] = (x.fiyat_2 == f).astype(int) - (x.fiyat_1 == f).astype(int)
    return x


def h5(x: pd.DataFrame) -> dict:
    w = stats.wilcoxon(x.delta, alternative="greater")
    terimler = " + ".join([c for c in x.columns if c.startswith("d_")])
    m = smf.ols(f"delta ~ ara_yil + {terimler}", data=x).fit(cov_type="HC1")
    b, (lo, hi) = m.params["Intercept"], m.conf_int().loc["Intercept"]
    return {"n_cift": len(x), "medyan_delta": float(x.delta.median()), "iyilesen_pay": float((x.delta > 0).mean()), "wilcoxon_p": float(w.pvalue),
            "fd_sabit": float(b), "fd_alt": float(lo), "fd_ust": float(hi), "fd_p": float(m.pvalues["Intercept"]),
            "fd_yuzde": float((np.exp(b) - 1) * 100), "ara_yil_katsayi": float(m.params["ara_yil"])}  # fmt: skip


def main() -> None:
    stil()
    t = yukle()
    a = hazirla(orneklem(t))
    x = ciftler(t, a)
    ana = h5(x)
    ana["karar"] = "desteklendi" if (ana["wilcoxon_p"] < 0.05 and ana["fd_sabit"] > 0 and ana["fd_p"] < 0.05) else "desteklenmedi"
    duy = {"ikinci_organik_degil": h5(ciftler(t, a, organik_ikinci=False)), "sadece_sabit_kimlik": h5(ciftler(t, a, sadece_id=True)),
           "sadece_tam_seri": h5(ciftler(t, a, sadece_hist=True))}  # fmt: skip
    tab = x.groupby("kademe_1", observed=True).agg(cift=("delta", "size"), medyan_delta=("delta", "median"), iyilesen=("delta", lambda v: (v > 0).mean()))

    gecis = pd.crosstab(x.kademe_1, x.kademe_2, normalize="index") * 100
    gecis = gecis.reindex(index=list(KADEME_AD), columns=list(KADEME_AD)).fillna(0)
    n1 = x.kademe_1.value_counts().reindex(list(KADEME_AD)).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    im = ax.imshow(gecis.values, cmap="Blues", vmin=0, vmax=70, aspect="auto")
    for i in range(5):
        for j in range(5):
            v = gecis.iat[i, j]
            ax.text(j, i, f"%{v:.0f}", ha="center", va="center", fontsize=10, color="white" if v > 40 else MUREKKEP, fontweight="bold" if i == j else "normal")
    ax.set_xticks(range(5), [KADEME_AD[k].replace(" · ", "\n") for k in KADEME_AD], fontsize=8.5)
    ax.set_yticks(range(5), [f"{KADEME_AD[k]}  (n={n1[k]:,})" for k in KADEME_AD], fontsize=8.5)
    ax.set_xlabel("İkinci oyunun kademesi")
    ax.set_ylabel("İlk oyunun kademesi")
    ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cb.outline.set_visible(False)
    t0 = gecis.loc["T0"]
    baslik(fig, f"İlk oyunu görünmez kalan stüdyoların %{100 - t0['T0']:.0f}'i ikinci oyunda 10+ incelemeye çıkıyor",
           f"{len(x):,} stüdyonun ilk iki oyunu. Her satır %100: ilk oyunu o kademede olanların ikinci oyunu nereye düştü? Köşegen (kalın) = aynı kademe.")  # fmt: skip
    fig.subplots_adjust(top=0.82, left=0.27)
    kaydet(fig, "M6_1_kademe_gecis", gecis.round(2).assign(n=n1), KAYNAK)

    fig, ax = plt.subplots(figsize=(9, 4.4))
    y = np.arange(len(tab))[::-1]
    deg = (np.exp(tab.medyan_delta) - 1) * 100
    ax.barh(y, deg, color=[KATEGORIK[0] if v > 0 else KATEGORIK[1] for v in deg], height=0.6)
    for yi, v, iy, n in zip(y, deg, tab.iyilesen, tab.cift):
        # sabit konum (sıfırın sağı): çubuk uzunluğundan bağımsız, eksen etiketine taşmaz
        ax.text(max(v, 0) + 4, yi, f"{v:+.0f}%  · iyileşen %{iy * 100:.0f}  (n={n:,})", va="center", ha="left", fontsize=9, color=MUREKKEP)
    ax.axvline(0, color=SOLUK, linewidth=1)
    ax.set_yticks(y, [KADEME_AD[k] for k in tab.index])
    ax.set_xlim(min(deg.min(), 0) - 8, max(deg.max(), 0) + 95)  # sağda etiket alanı
    ax.set_xlabel("İkinci oyunda ilk yıl incelemesindeki ortanca değişim (%)")
    ax.grid(axis="y", visible=False)
    sonuc = "DESTEKLENDİ" if ana["karar"] == "desteklendi" else "DESTEKLENMEDİ"
    temiz = duy["sadece_tam_seri"]["fd_yuzde"]
    baslik(fig, f"H5 {sonuc}: ikinci oyun ilkinden daha başarılı değil (ortalama {ana['fd_yuzde']:+.0f}%, en temiz ölçümde {temiz:+.0f}%)",
           f"{ana['n_cift']:,} stüdyo; iyileşen pay %{ana['iyilesen_pay'] * 100:.0f}, Wilcoxon p={ana['wilcoxon_p']:.2g}. Üst kademelerde düşüş kısmen ortalamaya dönüş: çok iyi bir ilk oyunu aşmak zor.")  # fmt: skip
    fig.subplots_adjust(top=0.8, left=0.2)
    kaydet(fig, "M6_2_H5_ikinci_oyun", tab.round(4), KAYNAK)

    ozet = {"H5": ana, "duyarlilik": duy, "kademe_tablosu": tab.round(4).to_dict("index"), "gecis": gecis.round(2).to_dict()}
    (KOK / "analysis" / "sonuclar" / "M6_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: ozet[k] for k in ("H5", "duyarlilik", "kademe_tablosu")}, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
