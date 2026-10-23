"""M2 ek · H6 ters nedensellik kontrolü: başarılı oyunlar Çince desteğini çıkıştan SONRA mı ekliyor?

Kullanım: python analysis/m2b_cince_ters_nedensellik.py
Veri: Şubat durumu = FronkonGames supported_languages (oyun başına alanları Şubat 2026'da donmuş: Z02Z 2026-02 kopyasıyla
      122.876 oyunda dil ve inceleme sayıları %100 aynı); Ekim durumu = kendi GetItems çekimimiz (2026-10-22, elanguage 6).
      İlk sürüm iki "ayrı" set kullandı ve sıfır ekleme buldu; setlerin aynı olduğu anlaşıldı, test bu kaynaklarla yeniden kuruldu.
      Ölçüm farkı tabanı: Şubat'ta var, Ekim'de yok (kaldırma ya da eşleme farkı) yönündeki uyuşmazlık da raporlanır.
Test 1: 8 ayda Çince EKLEYEN oyunların payı başarı kademesine göre (ekleme başarıyla artıyorsa ters nedensellik var).
Test 2: 2025 kohortunda H6 modeli Şubat durumuyla (çıkışa daha yakın) ve Ekim durumuyla; etki Şubat'ta belirgin küçülüyorsa
        Ekim tahmini başarı sonrası çeviriyi de içeriyor demektir.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import KADEME_AD, KATEGORIK, KOK, MUREKKEP, baslik, kaydet, orneklem, stil, yukle
from ortak_model import KONTROL, hazirla, katsayi, ols

KAYNAK = "Kaynak: FronkonGames (Şubat 2026 donmuş alanlar) ve Steam GetItems (Ekim 2026); Discovery Dynamics analizi."


def cince(yol: str) -> pd.Series:
    f = pd.read_parquet(KOK / yol, columns=["appID", "supported_languages"])
    f["appid"] = pd.to_numeric(f.appID, errors="coerce")
    f = f.dropna(subset=["appid"]).drop_duplicates("appid")
    return pd.Series(
        f.supported_languages.map(lambda v: v is not None and any("Simplified Chinese" in str(x) for x in v)).values, index=f.appid.astype(int).values
    )


def main() -> None:
    stil()
    subat = cince("data/raw/fronkongames/2026-10-15/games.parquet")
    d = hazirla(orneklem(yukle()))
    d = d[d.appid.isin(subat.index)].copy()
    d["cin_subat"], d["cin_ekim"] = d.appid.map(subat).astype(int), d.schinese.astype(int)
    taban = int(((d.cin_subat == 1) & (d.cin_ekim == 0)).sum())
    d["ekledi"] = (d.cin_subat == 0) & (d.cin_ekim == 1)
    risk = d[d.cin_subat == 0]
    g = risk.groupby("kademe", observed=True).agg(ekleyen=("ekledi", "mean"), n=("ekledi", "size"))
    g["ekleyen"] *= 100

    fig, ax = plt.subplots(figsize=(9, 4.4))
    x = np.arange(len(g))
    ax.bar(x, g.ekleyen, color=KATEGORIK[0], width=0.6)
    for xi, (v, n) in enumerate(zip(g.ekleyen, g.n)):
        ax.text(xi, v, f"%{v:.1f}\n(n={n:,})", ha="center", va="bottom", fontsize=8.5, color=MUREKKEP)
    ax.set_xticks(x, [KADEME_AD[k] for k in g.index], fontsize=8.8)
    ax.set_ylabel("Şubat'ta Çince yokken Ekim'e kadar ekleyenler (%)")
    ax.set_ylim(0, g.ekleyen.max() * 1.35)
    ax.grid(axis="x", visible=False)
    kat = g.ekleyen.iloc[-1] / max(g.ekleyen.iloc[0], 1e-9)
    baslik(fig, f"Başarılı oyunlar Çince desteğini sonradan daha sık ekliyor (en üst kademe, en alttakinin {kat:.0f} katı)",
           "8 ayda (Şubat → Ekim 2026) Çince ekleyen bağımsız oyunların payı, ilk yıl başarı kademesine göre. Ters nedensellik işareti.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M2_5_H6_ters_nedensellik", g.round(3), KAYNAK)

    k25 = d[d.yil == 2025]
    sonuc = {}
    for ad in ("cin_subat", "cin_ekim"):
        k = katsayi(ols(f"y_log ~ {ad} + {KONTROL}", k25), ad)
        sonuc[ad] = {"yuzde": round((np.exp(k["tahmin"]) - 1) * 100, 1), "alt": round((np.exp(k["alt"]) - 1) * 100, 1), "ust": round((np.exp(k["ust"]) - 1) * 100, 1), "n": k["n"]}  # fmt: skip
    hepsi = {ad: round((np.exp(katsayi(ols(f"y_log ~ {ad} + {KONTROL}", d), ad)["tahmin"]) - 1) * 100, 1) for ad in ("cin_subat", "cin_ekim")}
    ozet = {"ekleme_kademe": g.round(3).to_dict(), "kohort2025": sonuc, "tum_kohort_yuzde": hepsi, "n_eslesen": len(d),
            "ekleyen_toplam": int(d.ekledi.sum()), "ters_yon_taban": taban}  # fmt: skip
    (KOK / "analysis" / "sonuclar" / "M2b_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
