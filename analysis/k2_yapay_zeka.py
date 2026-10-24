"""K2 (keşifsel) · Yapay zekâ içerik beyanı ile sonuçlar.

Kullanım: python analysis/k2_yapay_zeka.py
Ölçü: IGDB anahtar kelimeleri "ai-generated …" (Steam'in Ocak 2024'te başlattığı beyan kategorileriyle birebir: artwork, music, voices,
    translations, marketing, coding…; IGDB beyanı aktarıyor görünüyor). Steam API'leri beyanı döndürmüyor (appdetails ile kontrol edildi);
    mağaza HTML'i taranmadı (kaynak politikası).
Örneklem: 2024–2025, analiz örneklemi, IGDB'de anahtar kelimesi kodlanmış oyunlar ("yok" ile "bilinmiyor" karışmasın).
Sınırlar: yalnız beyan edenler ölçülür; IGDB kodlaması başarıyla ilişkili (T13). Keşifsel; Holm ailesi dışında.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, baslik, kaydet, orneklem, stil, wilson, yukle
from ortak_model import KONTROL, hazirla, katsayi, logit

KAYNAK = "Kaynak: Steam; IGDB (yapay zekâ beyanı anahtar kelimeleri); Discovery Dynamics analizi."
AI_DESEN = r"\bai[- ]generat|generative ai"


def main() -> None:
    stil()
    oz = pd.read_parquet(KOK / "data" / "interim" / "oyun_igdb_ozellik.parquet")
    an = oz[oz.alan == "anahtar"]
    ai = an[an.ad.str.contains(AI_DESEN, case=False, regex=True, na=False) & ~an.ad.str.contains("no generative", case=False, na=False)]
    tur = ai.assign(tip=np.where(ai.ad.str.contains("artwork|concept|video", case=False), "gorsel", "diger")).groupby("appid").tip.agg(set)
    t = yukle()
    kodlu = set(an.appid)

    k = t[t.kohort].assign(kodlu=lambda d: d.appid.isin(kodlu), ai=lambda d: d.appid.isin(ai.appid))
    pay = k[k.kodlu].groupby("yil").ai.mean() * 100
    a = hazirla(orneklem(t))
    a = a[a.yil.isin([2024, 2025]) & a.appid.isin(kodlu)].copy()
    a["ai"] = a.appid.isin(ai.appid).astype(int)
    a["gorunmez"] = (a.reviews_365 < 10).astype(int)
    a["sevilen"] = (a.basari_sinifi == "sevilen_hit").astype(int)
    a["sadece_gorsel"] = a.appid.map(tur).map(lambda s: s == {"gorsel"} if isinstance(s, set) else False)

    g = a.groupby("ai").agg(n=("appid", "size"), gorunmez=("gorunmez", "mean"), hit=("y_hit", "mean"), sevilen=("sevilen", "mean"),
                            olumlu=("olumlu_oran_365", "median"))  # fmt: skip
    m = {y: katsayi(logit(f"{y} ~ ai + {KONTROL}", a), "ai", us=True) for y in ("gorunmez", "y_hit", "sevilen")}
    b50 = a[a.reviews_365 >= 50]
    olumlu_fark = float(b50[b50.ai == 1].olumlu_oran_365.median() - b50[b50.ai == 0].olumlu_oran_365.median()) if len(b50) else np.nan

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={"width_ratios": [1, 1.5]})
    yil = pay.loc[2021:]
    a1.bar(yil.index, yil.values, color=KATEGORIK[0], width=0.6)
    for x, v in yil.items():
        a1.text(x, v, f"%{v:.1f}", ha="center", va="bottom", fontsize=9, color=MUREKKEP)
    a1.set_title("Yapay zekâ beyanı olan oyunların payı (%)\n(IGDB'de anahtar kelimesi kodlanmış oyunlar içinde)", fontsize=10)
    a1.set_xticks(yil.index)
    a1.set_yticks([])
    a1.grid(False)
    olcu = [("gorunmez", "Görünmez\n(<10 inceleme)"), ("hit", "Hit\n(500+)"), ("sevilen", "Sevilen hit")]
    x = np.arange(len(olcu))
    for i, (e, ad) in enumerate([(0, "Beyan yok"), (1, "Yapay zekâ beyanı var")]):
        r = g.loc[e]
        deg = [r[c] * 100 for c, _ in olcu]
        k_ = [r[c] * r.n for c, _ in olcu]
        lo, hi = wilson(pd.Series(k_), pd.Series([r.n] * 3))
        a2.bar(x + (i - 0.5) * 0.36, deg, width=0.34, color=KATEGORIK[i], label=f"{ad} (n={int(r.n):,})",
               yerr=[np.array(deg) - lo.values * 100, hi.values * 100 - np.array(deg)], capsize=3, error_kw={"elinewidth": 1, "ecolor": IKINCIL})  # fmt: skip
        for xi, v, h in zip(x, deg, hi.values * 100):
            a2.text(xi + (i - 0.5) * 0.36, h + 1.2, f"%{v:.1f}", ha="center", fontsize=8.5, color=MUREKKEP)  # GA üst ucunun üstünde
    a2.set_xticks(x, [ad for _, ad in olcu])
    a2.set_ylabel("Oyunların yüzdesi")
    a2.legend(loc="upper right", fontsize=8.5)
    a2.grid(axis="x", visible=False)
    baslik(fig, f"KEŞİFSEL: Yapay zekâ beyan eden oyunlar daha sık görünmez kalıyor (OR {m['gorunmez']['tahmin']:.2f}), daha az hit oluyor (OR {m['y_hit']['tahmin']:.2f})",
           "2024–2025 çıkışlı bağımsız oyunlar, IGDB'de anahtar kelimesi kodlanmış olanlar. OR: tür, fiyat, yıl, EA, dil kontrollü. Yalnız beyan edenler ölçülür; çizgiler %95 GA.")  # fmt: skip
    fig.subplots_adjust(top=0.78, wspace=0.25)
    kaydet(fig, "K2_1_yapay_zeka", g.round(4), KAYNAK)

    ozet = {"pay_yil": pay.round(2).to_dict(), "tablo": g.round(4).to_dict("index"), "OR": m, "olumlu_medyan_farki_50plus": olumlu_fark,
            "n": len(a), "n_ai": int(a.ai.sum()), "sadece_gorsel_ai": int(a.sadece_gorsel.sum())}  # fmt: skip
    (KOK / "analysis" / "sonuclar" / "K2_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
