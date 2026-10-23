"""M2 · İçerik DNA'sı. Doğrulayıcı: H6 (Basitleştirilmiş Çince), H7 (doygunluk). Keşifsel: etiket etkileri, motivasyon fırsat haritası.

Kullanım: python analysis/m2_icerik.py
H6 (HIPOTEZLER): log(1+reviews_365) ~ schinese + standart kontroller; duyarlılık: eğilim skoru eşleştirmesi (tür × fiyat birebir,
    katman içinde logit PS en yakın, yerine koyarak, kaliper 0,2 SD), denge |SMD| < 0,1 tüm kontrollerde. Yan kanıt (Çince inceleme payı) inceleme dili verisi olmadığından test edilemedi.
H7: hit ~ log(1+kombo_12ay) + C(ana_tur) + standart kontroller; katsayı < 0 beklenir. Duyarlılık: benzer_12ay.
Keşifsel etiket etkileri R4'e açıktır (başarılı oyunlar daha çok/spesifik etiket alır); BH düzeltmeli q raporlanır.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, YUZEY, baslik, kaydet, orneklem, stil, yukle
from m2b_cince_ters_nedensellik import cince
from matplotlib.ticker import NullFormatter
from ortak_model import KONTROL, TURLER, hazirla, katsayi, logit, ols
from statsmodels.stats.multitest import multipletests

KAYNAK = "Kaynak: Steam, IGDB; Discovery Dynamics analizi. Başarı = ilk 365 gün inceleme."
RNG = np.random.default_rng(20261024)


def psm(d: pd.DataFrame, tedavi: str, sonuc: str) -> dict:
    """Tür kombinasyonu × fiyat bandında birebir; katman içinde logit PS'de en yakın kontrol (yerine koyarak, kaliper 0,2 SD).
    İlk sürüm (yalnız PS) Action/RPG'de SMD 0,17 verdi (< 0,1 ölçütü tutmadı) → birebir katman eklendi (2026-10-24)."""
    ps = smf.logit(f"{tedavi} ~ {KONTROL}", data=d).fit(disp=0)
    d = d.assign(lp=np.log(ps.predict(d) / (1 - ps.predict(d))))
    d["katman"] = d[TURLER].astype(int).astype(str).agg("".join, axis=1) + "|" + d.fiyat
    kaliper = 0.2 * d.lp.std()
    ciftler = []
    for _, g in d.groupby("katman"):
        t, c = g[g[tedavi] == 1], g[g[tedavi] == 0]
        if t.empty or c.empty:
            continue
        cs = c.sort_values("lp")
        lcs = cs.lp.values
        j = np.clip(np.searchsorted(lcs, t.lp.values), 1, max(len(lcs) - 1, 1)) if len(lcs) > 1 else np.zeros(len(t), int)
        sec = np.where(np.abs(lcs[np.maximum(j - 1, 0)] - t.lp.values) <= np.abs(lcs[j] - t.lp.values), np.maximum(j - 1, 0), j) if len(lcs) > 1 else j
        tut = np.abs(lcs[sec] - t.lp.values) <= kaliper
        ciftler.append((t[tut], cs.iloc[sec[tut]]))
    tt = pd.concat([a for a, _ in ciftler])
    cc = pd.concat([b for _, b in ciftler])
    fark = tt[sonuc].values - cc[sonuc].values
    boot = [RNG.choice(fark, len(fark)).mean() for _ in range(1000)]
    fiyat = pd.get_dummies(pd.concat([tt.fiyat, cc.fiyat]), prefix="fiyat").astype(float)
    ft, fc = fiyat.iloc[: len(tt)], fiyat.iloc[len(tt) :]
    smd = {}
    for v in ["yil", "log_dil", "ea", *TURLER]:
        s = np.sqrt((tt[v].var() + cc[v].var()) / 2)
        smd[v] = float(abs(tt[v].mean() - cc[v].mean()) / s) if s > 0 else 0.0
    for v in fiyat.columns:
        s = np.sqrt((ft[v].var() + fc[v].var()) / 2)
        smd[v] = float(abs(ft[v].mean() - fc[v].mean()) / s) if s > 0 else 0.0
    return {"ATT": float(fark.mean()), "alt": float(np.percentile(boot, 2.5)), "ust": float(np.percentile(boot, 97.5)), "n_tedavi": len(tt),
            "dislanan": int((d[tedavi] == 1).sum() - len(tt)), "maks_SMD": round(max(smd.values()), 4), "SMD": {k: round(v, 4) for k, v in smd.items()}}  # fmt: skip


def h6(d: pd.DataFrame) -> dict:
    d = d.assign(cin=d.schinese.astype(int))
    m = ols(f"y_log ~ cin + {KONTROL}", d)
    k = katsayi(m, "cin")
    hk = katsayi(logit(f"y_hit ~ cin + {KONTROL}", d), "cin", us=True)
    p = psm(d.reset_index(drop=True), "cin", "y_log")
    ucretli = katsayi(ols(f"y_log ~ cin + {KONTROL}", d[d.fiyat != "f2p"]), "cin")
    yuzde = lambda b: (np.exp(b) - 1) * 100
    subat = cince("data/raw/fronkongames/2026-10-15/games.parquet")  # Şubat 2026'da donmuş alanlar (bkz. m2b)
    k25 = d[(d.yil == 2025) & d.appid.isin(subat.index)].assign(cin_s=lambda x: x.appid.map(subat).astype(int))
    yakin = katsayi(ols(f"y_log ~ cin_s + {KONTROL}", k25), "cin_s")
    tab = pd.DataFrame(
        {"tahmin": [yuzde(k["tahmin"]), yuzde(ucretli["tahmin"]), yuzde(p["ATT"]), yuzde(yakin["tahmin"])],
         "alt": [yuzde(k["alt"]), yuzde(ucretli["alt"]), yuzde(p["alt"]), yuzde(yakin["alt"])],
         "ust": [yuzde(k["ust"]), yuzde(ucretli["ust"]), yuzde(p["ust"]), yuzde(yakin["ust"])]},
        index=["Ana model (tüm bağımsız oyunlar)", "Yalnız ücretli oyunlar", "Eğilim skoru eşleştirmesi", "Çıkışa en yakın dil durumu (2025)"],
    )  # fmt: skip
    fig, ax = plt.subplots(figsize=(9, 4.8))
    y = np.arange(len(tab))[::-1]
    ax.hlines(y, tab.alt, tab.ust, color=KATEGORIK[0], linewidth=2.5)
    ax.scatter(tab.tahmin, y, color=KATEGORIK[0], s=50, zorder=3, edgecolor=YUZEY, linewidth=1.5)
    for yi, (_, r) in zip(y, tab.iterrows()):
        ax.text(r.ust + 1, yi, f"+%{r.tahmin:.0f}  (%95 GA: {r.alt:.0f}–{r.ust:.0f})", va="center", fontsize=9, color=MUREKKEP)
    ax.axvline(0, color=SOLUK, linewidth=1)
    ax.set_yticks(y, tab.index)
    ax.set_xlim(min(0, tab.alt.min()) - 5, tab.ust.max() * 1.6)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("İlk yıl inceleme sayısındaki fark (%), diğer her şey sabitken")
    baslik(fig, f"H6: Çince desteği ~%{tab.tahmin.iloc[-1]:.0f}–{tab.tahmin.iloc[0]:.0f} daha fazla inceleme ile birlikte; bir kısmı sonradan çeviri",
           f"Kontroller: yıl, tür, fiyat, Early Access, dil sayısı. Eşleştirme dengesi: en büyük SMD {p['maks_SMD']:.3f} (< 0,1).\n"
           "Başarılı oyunlar Çince'yi sonradan ekliyor (M2_5); en alttaki satır çıkışa en yakın dil durumunu kullanır, en temkinli tahmindir.")  # fmt: skip
    fig.subplots_adjust(top=0.76, left=0.33)
    kaydet(fig, "M2_1_H6_cince", tab.round(2), KAYNAK + " İlişki; PSM gözlenen kontrollerle sınırlı.")
    return {"ols_log": k, "logit_hit_OR": hk, "ucretli_ols": ucretli, "psm": p, "cikisa_yakin_2025": yakin, "yuzde_tablo": tab.round(2).to_dict()}


def h7(d: pd.DataFrame) -> dict:
    d = d[d.kombo_12ay.notna()].copy()
    d["log_doy"] = np.log1p(d.kombo_12ay.astype(float))
    d["log_benzer"] = np.log1p(d.benzer_12ay.astype(float))
    m = logit(f"y_hit ~ log_doy + C(ana_tur) + {KONTROL}", d)
    k = katsayi(m, "log_doy", us=True)
    db = d[d.benzer_12ay.notna()]
    kb = katsayi(logit(f"y_hit ~ log_benzer + C(ana_tur) + {KONTROL}", db), "log_benzer", us=True)
    d["dilim"] = pd.qcut(d.kombo_12ay.astype(float).rank(method="first"), 10, labels=False)
    g = d.groupby("dilim").agg(orta=("kombo_12ay", "median"), hit=("y_hit", "mean"), n=("y_hit", "size"))
    g["hit"] *= 100
    fig, ax = plt.subplots(figsize=(9, 4.6))
    gx = g.orta.astype(float) + 1  # log eksende 0 çizilemez; ilk dilimin ortancası 0 → "1 + sayı" (nokta sessizce düşüyordu)
    ax.plot(gx, g.hit, color=KATEGORIK[0], marker="o", markersize=7)
    for x, v in zip(gx.iloc[[0, -1]], g.hit.iloc[[0, -1]]):
        ax.annotate(f"%{v:.1f}", (x, v), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9, color=MUREKKEP)
    ax.set_xscale("log")
    ax.set_xticks([1, 3, 10, 30, 100, 300], ["1", "3", "10", "30", "100", "300"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("1 + aynı tür ikilisinde son 12 ayda çıkan oyun sayısı (log; her nokta oyunların %10'u)")
    ax.set_ylabel("Hit oranı (%)")
    ax.set_ylim(0, g.hit.max() * 1.3)
    baslik(fig, "H7 desteklenmedi: kalabalık türler genelde daha az hit, ama aynı tür içinde kalabalık kombinasyon dezavantaj değil",
           f"Çizgi: ham hit oranları (%{g.hit.iloc[0]:.1f} → %{g.hit.iloc[-1]:.1f}). Tür sabit etkisi ve kontrollerle aynı tür içinde: OR {k['tahmin']:.2f} / log birim "
           f"(%95 GA {k['alt']:.2f}–{k['ust']:.2f}). Ön kayıt negatif katsayı bekliyordu.")  # fmt: skip
    fig.subplots_adjust(top=0.8)
    kaydet(fig, "M2_2_H7_doygunluk", g.round(3), KAYNAK)
    return {"kombo_OR": k, "benzer_OR": kb}


def etiket_etkileri(d: pd.DataFrame) -> dict:
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "tagid", "sira"])
    ic = tx[tx.boyut.isin(["A_tur", "B_mekanik", "C_gorsel", "D_tema", "E_oyuncu", "F_kapsam"])]
    e = e.merge(ic[["tagid", "ad", "boyut"]], on="tagid").sort_values(["appid", "sira"])
    e = e[e.groupby("appid").cumcount() < 10]  # oyunun ilk 10 içerik etiketi (R4: sıra, oy değil)
    hedef = ic[ic.boyut.isin(["B_mekanik", "C_gorsel", "E_oyuncu"])]
    say = e[e.appid.isin(d.appid) & e.tagid.isin(hedef.tagid)].groupby("ad").appid.nunique()
    secili = say[say >= 500].index
    sat = []
    for ad in secili:
        d["var"] = d.appid.isin(e.appid[e.ad == ad]).astype(int)
        k = katsayi(logit(f"y_hit ~ var + {KONTROL}", d), "var", us=True)
        sat.append({"etiket": ad, "boyut": hedef.set_index("ad").boyut.get(ad), "oyun": int(say[ad]), **k})
    t = pd.DataFrame(sat)
    t["q"] = multipletests(t.p, method="fdr_bh")[1]
    t = t.sort_values("tahmin")
    goster = pd.concat([t.head(10), t.tail(12)])
    fig, ax = plt.subplots(figsize=(9, 8))
    y = np.arange(len(goster))
    renk = [KATEGORIK[0] if v > 1 else KATEGORIK[1] for v in goster.tahmin]
    ax.hlines(y, goster.alt, goster.ust, color=renk, linewidth=2)
    ax.scatter(goster.tahmin, y, color=renk, s=34, zorder=3, edgecolor=YUZEY, linewidth=1.2)
    ax.axvline(1, color=SOLUK, linewidth=1)
    ax.set_xscale("log")
    ax.set_xticks([0.25, 0.5, 1, 2, 4], ["×0,25", "×0,5", "×1", "×2", "×4"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(y, [f"{a}  ({b.split('_')[1]})" for a, b in zip(goster.etiket, goster.boyut)], fontsize=8.8)
    ax.grid(axis="y", visible=False)
    ax.axhline(9.5, color="#e1e0d9", linewidth=6)
    ax.set_xlabel("Hit olma ihtimali (diğer her şey sabitken, kaç kat?)")
    baslik(fig, "KEŞİFSEL: Hangi mekanik, görsel ve oyuncu yapısı etiketleri başarıyla birlikte görülüyor?",
           f"{len(t)} etiket test edildi (her biri ≥500 oyunda); en güçlü 12 olumlu ve 10 olumsuz. Etiketler oyuncu oyuyla şekillenir (R4): başarı etiketleri de etkileyebilir.")  # fmt: skip
    fig.subplots_adjust(top=0.86, left=0.3)
    kaydet(fig, "M2_3_etiket_etkileri", t.set_index("etiket").round(4), KAYNAK + " Benjamini–Hochberg q değerleri CSV'de.")
    return {"test_sayisi": len(t), "q<0.05": int((t.q < 0.05).sum()), "en_olumlu": t.tail(5)[["etiket", "tahmin"]].round(2).values.tolist(),
            "en_olumsuz": t.head(5)[["etiket", "tahmin"]].round(2).values.tolist()}  # fmt: skip


def motivasyon(d: pd.DataFrame) -> dict:
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv").dropna(subset=["motivasyon"])
    e = pd.read_parquet(KOK / "data" / "interim" / "oyun_etiket.parquet", columns=["appid", "tagid", "sira"])
    e = e[e.appid.isin(d.appid)].merge(tx[["tagid", "motivasyon"]], on="tagid").sort_values(["appid", "sira"])
    e = e[e.groupby("appid").cumcount() < 10]
    e["w"] = (11 - e.groupby("appid").cumcount().add(1)) / 10
    e = e.assign(motivasyon=e.motivasyon.str.split(";")).explode("motivasyon")
    e["w"] /= e.groupby(["appid", "tagid"]).w.transform("size")
    prof = e.pivot_table(index="appid", columns="motivasyon", values="w", aggfunc="sum", fill_value=0)
    prof = prof.div(prof.sum(axis=1), axis=0)
    baskin = prof.idxmax(axis=1).rename("baskin")
    x = d.merge(baskin, left_on="appid", right_index=True)
    g = x.groupby("baskin").agg(arz=("appid", "size"), hit=("y_hit", "mean"), sevilen=("basari_sinifi", lambda v: (v == "sevilen_hit").mean()))
    g["arz"] = g.arz / g.arz.sum() * 100
    g[["hit", "sevilen"]] *= 100
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(g.arz, g.hit, s=90, color=KATEGORIK[0], edgecolor=YUZEY, linewidth=1.5, zorder=3)
    for m, r in g.iterrows():
        ax.annotate(m, (r.arz, r.hit), xytext=(7, 4), textcoords="offset points", fontsize=9, color=MUREKKEP)
    ax.axhline(x.y_hit.mean() * 100, color=SOLUK, linewidth=1)
    ax.axvline(100 / len(g), color=SOLUK, linewidth=1)
    ax.set_xscale("log")
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks([1, 2, 5, 10, 20, 40], ["%1", "%2", "%5", "%10", "%20", "%40"])
    ax.set_xlabel("Arz: baskın motivasyonu bu olan oyunların payı (log)")
    ax.set_ylabel("Hit oranı (%)")
    ax.text(0.99, 0.98, "az arz, yüksek başarı\n= fırsat bölgesi", transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=IKINCIL)
    baslik(fig, "KEŞİFSEL: Oyuncu motivasyonu haritası, hangi ihtiyaç az karşılanıyor ama iyi karşılık buluyor?",
           "Her nokta bir motivasyon (Quantic Foundry). Oyunun baskın motivasyonu etiketlerinden hesaplandı. Eşleme tek kodlayıcı taslağı; ikinci kodlayıcı bekleniyor.")  # fmt: skip
    fig.subplots_adjust(top=0.85)
    kaydet(fig, "M2_4_motivasyon_haritasi", g.round(3), KAYNAK + " Ham oranlar; tür ve fiyat kontrolü yok.")
    return g.round(2).to_dict("index")


def main() -> None:
    stil()
    d = hazirla(orneklem(yukle()))
    ozet = {"n": len(d), "H6": h6(d), "H7": h7(d), "etiket": etiket_etkileri(d), "motivasyon": motivasyon(d)}
    (KOK / "analysis" / "sonuclar" / "M2_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: ozet[k] for k in ("n", "H6", "H7", "etiket")}, ensure_ascii=False, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
