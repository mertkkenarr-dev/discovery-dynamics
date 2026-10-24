"""K4 (keşifsel) · Çıkış öncesi tahmin modeli: yalnız çıkıştan önce bilinebilen niteliklerle hit olasılığı.

Kullanım: python analysis/k4_tahmin_modeli.py
Zamansal doğrulama (KAPSAM §6): eğitim ≤ 2023 (erken durdurma için ≤2022 eğitim / 2023 doğrulama, sonra ≤2023 ile yeniden), test 2024–2025.
Sızıntı kuralları (R4, R6):
  - Oyuncu etiketleri ve türevleri (novelty, kombo/benzer doygunluk) GİRMEZ: sonradan oylanır.
  - IGDB'den gelen HİÇBİR alan girmez: IGDB'nin kodlama yoğunluğu başarıyla ilişkili (T13); eksiklik deseni başarıyı sızdırır.
  - Model A: kesin + yaklaşık çıkış öncesi (mevcut fiyat, dil listesi, platform). Model B (katı): yalnız kesin çıkış öncesi.
  - Model C: A'dan dil bilgisi (Çince, dil sayısı) çıkarılmış; Çince sonradan ekleniyor (M2b), A'daki payı sızıntı olabilir.
Değerlendirme: PR-AUC (hit ~%5; doğruluk yanıltıcı), ROC-AUC, ondalık dilimlere göre isabet (lift). Katkılar: LightGBM SHAP (pred_contrib).
"""

from __future__ import annotations

import json

import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from grafik import IKINCIL, KATEGORIK, KOK, MUREKKEP, SOLUK, baslik, kaydet, orneklem, stil, yukle
from sklearn.metrics import average_precision_score, roc_auc_score

KAYNAK = "Kaynak: Steam; Discovery Dynamics analizi. LightGBM; eğitim ≤2023, test 2024–2025."
TURLER = ["Action", "Adventure", "Casual", "RPG", "Simulation", "Strategy", "Sports", "Racing", "Massively Multiplayer", "Indie"]
KESIN = ["f2p", "ea_ile_basladi", "demo_cikis_oncesi", "demo_gun_once", "playtest_var", "nextfest_aday", "ay", "haftanin_gunu", "ayni_hafta_cikan",
         "ayni_hafta_buyuk_yayinci", "gun_sonraki_indirim", "indirim_icinde", "yayinci_onceki_oyun", "gelistirici_onceki_oyun", "studyo_yasi_gun",
         "kendi_yayini", "n_gelistirici", "n_steam_tur", *[f"tur_{t}" for t in TURLER]]  # fmt: skip
YAKLASIK = ["fiyat_liste_usd", "n_dil", "schinese", "win", "mac", "linux"]
AD = {"fiyat_liste_usd": "Fiyat", "n_dil": "Dil sayısı", "schinese": "Çince desteği", "gelistirici_onceki_oyun": "Geliştiricinin önceki oyunları",
      "yayinci_onceki_oyun": "Yayıncının önceki oyunları", "studyo_yasi_gun": "Stüdyo yaşı", "kendi_yayini": "Kendi yayını", "ea_ile_basladi": "Early Access",
      "demo_cikis_oncesi": "Çıkış öncesi demo", "demo_gun_once": "Demo kaç gün önce", "nextfest_aday": "Next Fest (dolaylı)", "playtest_var": "Playtest",
      "ayni_hafta_cikan": "Aynı hafta çıkan oyun", "gun_sonraki_indirim": "Sonraki büyük indirime gün", "ay": "Çıkış ayı", "haftanin_gunu": "Çıkış günü",
      "n_steam_tur": "Tür sayısı", "f2p": "Ücretsiz", "mac": "macOS", "linux": "Linux", "win": "Windows", "n_gelistirici": "Geliştirici sayısı",
      "indirim_icinde": "İndirim sırasında çıkış", "ayni_hafta_buyuk_yayinci": "Aynı hafta büyük yayıncı"} | {f"tur_{t}": f"Tür: {t}" for t in TURLER}  # fmt: skip
PARAM = {"objective": "binary", "learning_rate": 0.03, "num_leaves": 31, "min_data_in_leaf": 100, "feature_fraction": 0.8, "bagging_fraction": 0.8,
         "bagging_freq": 1, "lambda_l2": 1.0, "verbose": -1, "seed": 20261024}  # fmt: skip


def veri() -> pd.DataFrame:
    a = orneklem(yukle())
    tr = pd.read_parquet(KOK / "data" / "interim" / "oyun_steam_tur.parquet")
    d = pd.crosstab(tr.appid, tr.tur.replace({"Free To Play": "Free to Play"})).clip(upper=1)
    for t in TURLER:
        a[f"tur_{t}"] = a.appid.map(d[t] if t in d else pd.Series(dtype=float)).fillna(0)
    for c in KESIN + YAKLASIK:
        if a[c].dtype == object or str(a[c].dtype) in ("boolean", "bool"):
            a[c] = a[c].astype(float)
    a["y"] = a.hit.astype(int)
    return a


def egit(a: pd.DataFrame, oz: list[str]) -> dict:
    tr, te = a[a.yil <= 2023], a[a.yil >= 2024]
    ic, dg = tr[tr.yil <= 2022], tr[tr.yil == 2023]
    m0 = lgb.train(PARAM, lgb.Dataset(ic[oz], ic.y), 2000, valid_sets=[lgb.Dataset(dg[oz], dg.y)], callbacks=[lgb.early_stopping(100, verbose=False)])
    m = lgb.train(PARAM, lgb.Dataset(tr[oz], tr.y), m0.best_iteration)
    p = m.predict(te[oz])
    return {"model": m, "p": p, "test": te, "pr_auc": float(average_precision_score(te.y, p)), "roc_auc": float(roc_auc_score(te.y, p)),
            "taban": float(te.y.mean()), "agac": int(m0.best_iteration)}  # fmt: skip


def main() -> None:
    stil()
    a = veri()
    A, B = egit(a, KESIN + YAKLASIK), egit(a, KESIN)
    C = egit(a, KESIN + [c for c in YAKLASIK if c not in ("schinese", "n_dil")])  # dil bilgisi sonradan ekleniyor (M2b) → sızıntı payı
    ANA = C  # ana model: dilsiz (Çince sonradan ekleniyor → A'daki dil payı kısmen sızıntı). A ve B üst/alt sınır.
    te = ANA["test"].assign(p=ANA["p"])
    te["dilim"] = pd.qcut(te.p.rank(method="first"), 10, labels=range(1, 11))
    lift = te.groupby("dilim", observed=True).y.mean() * 100

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.bar(lift.index.astype(int), lift.values, color=[KATEGORIK[0] if i >= 9 else "#9ec5f4" for i in lift.index.astype(int)], width=0.65)
    for x, v in lift.items():
        ax.text(int(x), v + 0.5, f"%{v:.1f}", ha="center", fontsize=8.5, color=MUREKKEP)
    ax.axhline(ANA["taban"] * 100, color=SOLUK, linewidth=1)
    ax.text(0.6, ANA["taban"] * 100 + 0.6, f"ortalama %{ANA['taban'] * 100:.1f}", fontsize=8.5, color=IKINCIL)
    ax.set_xticks(range(1, 11), ["1\nen düşük"] + [str(i) for i in range(2, 10)] + ["10\nen yüksek"])
    ax.set_xlabel("Modelin verdiği hit olasılığına göre oyun dilimleri (her dilim test oyunlarının %10'u)")
    ax.set_ylabel("Gerçekte hit olanlar (%)")
    ax.grid(axis="x", visible=False)
    kat = lift.iloc[-1] / (ANA["taban"] * 100)
    baslik(fig, f"KEŞİFSEL: Çıkış öncesi bilgilerle en umut verici %10, ortalamanın {kat:.1f} katı hit veriyor",
           f"Test: 2024–2025'te çıkan {len(te):,} bağımsız oyun (eğitim ≤2023). Ana model (dil bilgisi yok): PR-AUC {C['pr_auc']:.2f} (rastgele {C['taban']:.2f}), "
           f"ROC-AUC {C['roc_auc']:.2f}. Dil eklenince {A['pr_auc']:.2f} (kısmen sızıntı), fiyat da çıkarılınca {B['pr_auc']:.2f}.")  # fmt: skip
    fig.subplots_adjust(top=0.8, bottom=0.2)
    kaydet(fig, "K4_1_tahmin_isabeti", lift.round(3).to_frame("hit_orani"), KAYNAK)

    oz = KESIN + [c for c in YAKLASIK if c not in ("schinese", "n_dil")]
    katki = ANA["model"].predict(te[oz], pred_contrib=True)[:, :-1]
    onem = pd.Series(np.abs(katki).mean(axis=0), index=oz).sort_values(ascending=False).head(14)
    yon = pd.Series({c: np.corrcoef(te[c].fillna(te[c].median()), katki[:, oz.index(c)])[0, 1] for c in onem.index})
    fig, ax = plt.subplots(figsize=(9, 6))
    y = np.arange(len(onem))[::-1]
    ax.barh(y, onem.values, color=[KATEGORIK[0] if v > 0 else KATEGORIK[1] for v in yon.reindex(onem.index).fillna(0)], height=0.62)
    ax.set_yticks(y, [AD.get(c, c) for c in onem.index])
    ax.set_xlabel("Tahmine ortalama katkı (|SHAP|, log-olasılık)")
    ax.grid(axis="y", visible=False)
    ax.text(
        0.98, 0.04, "mavi: değer arttıkça olasılık artıyor\nturuncu: değer arttıkça azalıyor", transform=ax.transAxes, ha="right", fontsize=8.5, color=IKINCIL
    )
    baslik(fig, f"KEŞİFSEL: Tahmini en çok belirleyen çıkış öncesi bilgi: {AD.get(onem.index[0], onem.index[0]).lower()}",
           "Ana model (dil bilgisi yok), test oyunları. Katkı büyüklüğü neden-sonuç değil, tahmine yararlılıktır; fiyat kapsam ve bütçeyi de temsil eder. Yön: nitelik ile katkının korelasyonu.")  # fmt: skip
    fig.subplots_adjust(top=0.85, left=0.3)
    kaydet(fig, "K4_2_tahmin_katkilari", pd.DataFrame({"ort_abs_shap": onem, "yon_kor": yon}).round(4), KAYNAK)

    ozet = {k: {kk: v for kk, v in m.items() if kk in ("pr_auc", "roc_auc", "taban", "agac")} for k, m in (("A", A), ("B", B), ("C_dilsiz", C))}
    ozet |= {"lift": lift.round(3).to_dict(), "onem": onem.round(4).to_dict(), "n_test": len(te), "n_egitim": int((a.yil <= 2023).sum())}
    (KOK / "analysis" / "sonuclar" / "K4_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
