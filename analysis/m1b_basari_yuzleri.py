"""M1 ek · Başarının dört yüzü: görünürlük, beğeni, ticari, göreli. İkincil sonuç ailesi (HIPOTEZLER 2026-10-24).

Kullanım: python analysis/m1b_basari_yuzleri.py      (m1_gorunurluk.py ile aynı örneklem)
Sağlamlık: M1 modeli üç sonuçla tekrar kurulur (hit, sevilen_hit, göreli üst %10). Ticari başarı karşılaştırmaya girmez: fiyat gelir
formülünün içinde, fiyat katsayısı mekanik olarak şişer (döngüsellik).
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, YUZEY, baslik, kaydet, orneklem, stil, yukle
from m1_gorunurluk import KAYNAK, TURLER, turleri_ekle
from matplotlib.ticker import NullFormatter

SINIF = [("sevilen_hit", "Sevilen hit", "500+ inceleme, %80+ olumlu"), ("hit", "Hit", "500+ inceleme, %70–80 olumlu"),
         ("tartismali_hit", "Tartışmalı hit", "500+ inceleme, %70'ten az olumlu"), ("sessiz_basari", "Sessiz başarı", "50–499 inceleme, çok beğenilmiş"),
         ("orta", "Orta", "10–499 inceleme, diğer"), ("gorunmez", "Görünmez", "10'dan az inceleme")]  # fmt: skip


def f6_siniflar(a: pd.DataFrame) -> dict:
    p = a.basari_sinifi.value_counts(normalize=True) * 100
    p = p.reindex([s for s, _, _ in SINIF])
    fig, ax = plt.subplots(figsize=(9, 4.6))
    y = np.arange(len(SINIF))[::-1]
    vurgu = {"sevilen_hit", "sessiz_basari"}
    ax.barh(y, p.values, color=[KATEGORIK[0] if s in vurgu else "#c3c2b7" for s, _, _ in SINIF], height=0.6)
    for yi, v in zip(y, p.values):
        ax.text(v + 0.6, yi, f"%{v:.1f}", va="center", fontsize=10, color=MUREKKEP, fontweight="bold")
    ax.set_yticks(y, [f"{ad}\n{ac}" for _, ad, ac in SINIF], fontsize=8.8)
    ax.set_xlim(0, p.max() * 1.15)
    ax.set_xticks([])
    ax.grid(False)
    ax.spines["bottom"].set_visible(False)
    hit = p[["sevilen_hit", "hit", "tartismali_hit"]].sum()
    baslik(fig, f"Hit'lerin %{p['sevilen_hit'] / hit * 100:.0f}'ü gerçekten sevilen oyunlar; 'sessiz başarı' da bir o kadar yaygın",
           "Bağımsız oyunların başarı sınıfları. Mavi = beğeniyle tanımlanan iki başarı türü. Olumlu oran: ilk yılın incelemeleri.")  # fmt: skip
    fig.subplots_adjust(top=0.8, left=0.27)
    kaydet(fig, "M1_6_basari_siniflari", p.round(2).to_frame("yuzde"), KAYNAK)
    return {"sinif_yuzde": p.round(2).to_dict(), "hit_icinde_sevilen": round(p["sevilen_hit"] / hit * 100, 1)}


def f7_gorunurluk_para(a: pd.DataFrame) -> dict:
    d = a[a.brut_gelir_orta.notna() & (a.reviews_365 >= 1)].copy()
    hit, para = d.hit.astype(bool), d.ticari_basari.astype(bool)
    dort = {
        "hit_ve_para": int((hit & para).sum()),
        "hit_para_yok": int((hit & ~para).sum()),
        "para_hit_yok": int((~hit & para).sum()),
        "ikisi_yok": int((~hit & ~para).sum()),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(d.reviews_365, d.fiyat_liste_usd, s=3, color=SOLUK, alpha=0.18, linewidth=0, rasterized=True)
    ax.scatter(d.reviews_365[para & ~hit], d.fiyat_liste_usd[para & ~hit], s=5, color=KATEGORIK[1], alpha=0.6, linewidth=0, rasterized=True)
    ax.scatter(d.reviews_365[hit & ~para], d.fiyat_liste_usd[hit & ~para], s=5, color=KATEGORIK[0], alpha=0.6, linewidth=0, rasterized=True)
    ax.set_xscale("log")
    ax.set_yscale("log")
    x = np.logspace(0, 6, 200)
    ax.plot(x, 100_000 / (30 * x), color=MUREKKEP, linewidth=1.2)
    ax.axvline(500, color=MUREKKEP, linewidth=1.2)
    ax.set_xlim(1, d.reviews_365.max() * 1.5)
    ax.set_ylim(0.4, 120)
    ax.set_xticks([1, 10, 100, 500, 5000, 50000], ["1", "10", "100", "500", "5 bin", "50 bin"])
    ax.set_yticks([0.5, 1, 5, 10, 20, 50, 100], ["0,5", "1", "5", "10", "20", "50", "100"])
    ax.set_xlabel("İlk yıl inceleme sayısı (log)")
    ax.set_ylabel("Liste fiyatı, USD (log)")
    ax.text(520, 105, "hit eşiği\n(500 inceleme)", fontsize=8.5, color=IKINCIL, va="top")
    kutu = {"boxstyle": "round,pad=0.3", "facecolor": YUZEY, "edgecolor": "none", "alpha": 0.9}
    ax.text(4000, 100_000 / (30 * 4000) * 1.25, "≈100 bin USD\nbrüt gelir eğrisi", fontsize=8.5, color=IKINCIL, bbox=kutu)
    ax.text(
        1.15,
        95,
        f"Hit değil ama\n100 bin USD'yi geçti:\n{dort['para_hit_yok']:,} oyun",
        color=KATEGORIK[1],
        fontsize=9.5,
        fontweight="bold",
        va="top",
        bbox=kutu,
    )
    ax.text(
        1.15,
        0.45,
        f"Hit ama 100 bin\nUSD'nin altında:\n{dort['hit_para_yok']:,} oyun",
        color=KATEGORIK[0],
        fontsize=9.5,
        fontweight="bold",
        va="bottom",
        bbox=kutu,
    )
    pay = dort["para_hit_yok"] / (dort["para_hit_yok"] + dort["hit_ve_para"]) * 100
    baslik(fig, f"Görünürlük ≠ para: 100 bin USD'yi geçen oyunların %{pay:.0f}'i 'hit' sayılmıyor",
           "Her nokta bir ücretli bağımsız oyun. Brüt gelir ≈ inceleme × 30 × fiyat (kaba tahmin; Steam payı ve indirimler öncesi). Eğrinin üstü ≈ 100 bin USD+.")  # fmt: skip
    fig.subplots_adjust(top=0.85)
    kaydet(fig, "M1_7_gorunurluk_para", pd.Series(dort).to_frame("oyun"), KAYNAK + " Gelir tahmini kaba bir aralıktır.")
    return dort | {"para_icinde_hit_olmayan_yuzde": round(pay, 1)}


def model(d: pd.DataFrame, sonuc: str) -> pd.DataFrame:
    f = f"{sonuc} ~ C(fiyat, Treatment('5-10')) + ea + deneyimli + kendi + log_dil + " + " + ".join(TURLER) + " + C(yil)"
    m = smf.logit(f, data=d).fit(disp=0, cov_type="HC1")
    return pd.DataFrame({"OR": np.exp(m.params), "alt": np.exp(m.conf_int()[0]), "ust": np.exp(m.conf_int()[1])})


def f8_saglamlik(a: pd.DataFrame) -> dict:
    d = a[a.fiyat_bandi.notna() & ~a.f2p].copy()
    d["fiyat"] = d.fiyat_bandi.astype(str)
    d["ea"] = d.ea_ile_basladi.astype(int)
    d["deneyimli"] = (d.gelistirici_onceki_oyun >= 1).astype(int)
    d["kendi"] = d.kendi_yayini.eq(True).astype(int)
    d["log_dil"] = np.log1p(d.n_dil)
    d["y_hit"] = d.hit.astype(int)
    d["y_sevilen"] = (d.basari_sinifi == "sevilen_hit").astype(int)
    d["y_goreli"] = (d.goreli_yuzdelik >= 0.9).astype(int)
    terim = {"log_dil": "Dil sayısı (log)", "deneyimli": "Önceki oyunu var", "kendi": "Kendi yayını", "ea": "Early Access ile çıkış",
             "Simulation": "Tür: Simulation", "RPG": "Tür: RPG", "Casual": "Tür: Casual", "Sports": "Tür: Sports", "Racing": "Tür: Racing"}  # fmt: skip
    sonuclar = [("y_hit", "Hit (500+ inceleme)"), ("y_sevilen", "Sevilen hit (+%80 olumlu)"), ("y_goreli", "Yılı ve türünde ilk %10")]
    tab = pd.concat({ad: model(d, y).loc[list(terim)] for y, ad in sonuclar}, names=["sonuc", "terim"]).reset_index()
    tab["terim"] = tab.terim.map(terim)
    fig, ax = plt.subplots(figsize=(9, 6.2))
    sira = list(terim.values())[::-1]
    for i, (_, ad) in enumerate(sonuclar):
        t = tab[tab.sonuc == ad].set_index("terim").loc[sira]
        y = np.arange(len(sira)) + (1 - i) * 0.24
        ax.hlines(y, t.alt, t.ust, color=KATEGORIK[i], linewidth=2)
        ax.scatter(t.OR, y, color=KATEGORIK[i], s=34, zorder=3, edgecolor=YUZEY, linewidth=1.2, label=ad)
    ax.axvline(1, color=SOLUK, linewidth=1)
    ax.set_xscale("log")
    ax.set_xticks([0.25, 0.5, 1, 2, 4], ["×0,25", "×0,5", "×1", "×2", "×4"])
    ax.xaxis.set_minor_formatter(NullFormatter())  # log eksende "3×10⁻¹" gibi ara etiketler okuyucuya anlamsız
    ax.set_yticks(range(len(sira)), sira)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Başarı ihtimali (diğer her şey ve fiyat sabitken, kaç kat?)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=8.8)
    yon = tab.assign(yon=np.sign(np.log(tab.OR))).pivot(index="terim", columns="sonuc", values="yon")
    ayni = int((yon.nunique(axis=1) == 1).sum())
    baslik(fig, f"Bulgular başarının tanımına göre değişmiyor: {ayni}/{len(yon)} etkenin yönü üç tanımda da aynı",
           f"M1 modeli üç farklı başarı tanımıyla, n={len(d):,} ücretli bağımsız oyun. Fiyat ve çıkış yılı kontrol edildi.\n"
           "Yeşil ölçü türler arası farkı tanım gereği siler; tür satırlarında yeşil nokta 'aynı türdeki rakiplerine göre' okunmalı.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M1_8_saglamlik", tab.round(4).set_index(["sonuc", "terim"]), KAYNAK)
    return {"ayni_yon": f"{ayni}/{len(yon)}", "OR": tab.round(3).to_dict("records")}


def main() -> None:
    stil()
    a = turleri_ekle(orneklem(yukle()))
    ozet = {"siniflar": f6_siniflar(a), "gorunurluk_para": f7_gorunurluk_para(a), "saglamlik": f8_saglamlik(a)}
    (KOK / "analysis" / "sonuclar" / "M1b_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in ozet.items() if k != "saglamlik"} | {"ayni_yon": ozet["saglamlik"]["ayni_yon"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
