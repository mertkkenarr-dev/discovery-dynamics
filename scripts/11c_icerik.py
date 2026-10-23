"""11c: İçerik metrikleri — novelty_score (H1) ve doygunluk (H7).

Kullanım: cd scripts && python 11c_icerik.py        (10, r01, 11b'den sonra)
Çıktı   : interim/icerik.parquet  appid, n_icerik_etiket, novelty_k5/k10/k20, en_yakin_benzerlik, benzer_12ay_tXX, tur_kombo, kombo_12ay

Vektör : yalnız içerik etiketleri (config icerik_boyutlari; X_* ve H_teknik hariç), içerik etiketleri arasındaki sıraya göre
         ilk N, ağırlık (N+1-sıra)/N × IDF. Oy sayısı kullanılmaz (R4). IDF yalnız idf_bitis öncesi oyunlardan (sızıntısız).
Komşular: yalnız KESİN olarak daha önce çıkmış oyunlar (aynı gün dahil değil). Oyunlar tarihe göre sıralanır; her parti
         yalnız kendinden önceki satırlarla çarpılır, bu yüzden geleceğe ait bilgi yapısal olarak giremez.
Hipotez testi YOK.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from ortak import INTERIM, KOK, KararKaydi, ayarlar

PARTI = 512
ESIKLER = (0.4, 0.5, 0.6, 0.7)


def vektorler(o: pd.DataFrame, cfg: dict) -> tuple[np.ndarray, np.ndarray]:
    c = cfg["icerik"]
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    icerik = set(tx.tagid[tx.boyut.isin(c["icerik_boyutlari"])])
    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet", columns=["appid", "tagid", "sira"])
    e = e[e.tagid.isin(icerik) & e.appid.isin(o.appid)].sort_values(["appid", "sira"])
    e["isira"] = e.groupby("appid").cumcount() + 1  # içerik etiketleri arasındaki sıra
    n_etiket = e.groupby("appid").size()
    N = c["ilk_n_etiket"]
    e = e[e.isira <= N]
    # IDF: yalnız idf_bitis öncesi oyunlardan; sonradan doğan etiketler en yüksek IDF'yi alır (yumuşatılmış)
    eski = set(o.appid[o.cikis < pd.Timestamp(str(c["idf_bitis"]))])
    df = e[e.appid.isin(eski)].groupby("tagid").appid.nunique()
    n_eski = len(eski)
    idf = {t: np.log((n_eski + 1) / (df.get(t, 0) + 1)) + 1 for t in e.tagid.unique()}
    sutun = {t: i for i, t in enumerate(sorted(e.tagid.unique()))}
    satir = {a: i for i, a in enumerate(o.appid)}
    X = np.zeros((len(o), len(sutun)), dtype=np.float32)
    X[e.appid.map(satir).values, e.tagid.map(sutun).values] = ((N + 1 - e.isira) / N * e.tagid.map(idf)).values
    norm = np.linalg.norm(X, axis=1, keepdims=True)
    X = np.divide(X, norm, out=np.zeros_like(X), where=norm > 0)
    return X, o.appid.map(n_etiket).fillna(0).astype(int).values


def main() -> None:
    cfg, K = ayarlar(), KararKaydi("11c_icerik")
    c = cfg["icerik"]
    o = pd.read_parquet(INTERIM / "oznitelik.parquet", columns=["appid", "cikis", "kohort"])
    o = o[o.cikis.notna()].sort_values("cikis", kind="stable").reset_index(drop=True)
    X, n_et = vektorler(o, cfg)
    t = o.cikis.values.astype("datetime64[ns]")
    once = np.searchsorted(t, t, side="left")  # satır g için kesin olarak önceki satırlar: [0, once[g])
    yil_once = np.searchsorted(t, t - np.timedelta64(365, "D"), side="left")
    ks = c["novelty_k"]
    nov = {k: np.full(len(o), np.nan) for k in ks}
    en_yakin = np.full(len(o), np.nan)
    benzer = {s: np.zeros(len(o), dtype=np.int32) for s in ESIKLER}
    for i in range(0, len(o), PARTI):
        j = min(i + PARTI, len(o))
        ust = once[j - 1]
        if ust == 0:
            continue
        S = X[i:j] @ X[:ust].T
        kol = np.arange(ust)
        maske = kol[None, :] >= once[i:j, None]  # aynı gün ve sonrası
        S[maske] = -np.inf
        for s in ESIKLER:
            pencere = (kol[None, :] >= yil_once[i:j, None]) & ~maske
            benzer[s][i:j] = ((S >= s) & pencere).sum(axis=1)
        kmax = max(ks)
        if ust > kmax:
            idx = np.argpartition(-S, kmax - 1, axis=1)[:, :kmax]
            top = np.take_along_axis(S, idx, axis=1)
            top = -np.sort(-top, axis=1)
            en_yakin[i:j] = np.clip(top[:, 0], 0, 1)
            for k in ks:
                # k komşunun hepsi geçerli olmalı (−inf = kesin önceki oyun yok); float32 yuvarlaması 1,0000001 → kırp
                yeterli_k = np.isfinite(top[:, :k]).all(axis=1)
                nov[k][i:j] = np.where(yeterli_k, 1 - np.clip(top[:, :k], 0, 1).mean(axis=1), np.nan)
        if (i // PARTI) % 40 == 0:
            print(f"  {j:,}/{len(o):,}", flush=True)

    gecerli = (n_et >= c["min_etiket"]) & np.isfinite(nov[10])
    out = o[["appid"]].assign(n_icerik_etiket=n_et, en_yakin_benzerlik=np.where(gecerli, en_yakin, np.nan))
    for k in ks:
        out[f"novelty_k{k}"] = np.where(gecerli & np.isfinite(nov[k]), nov[k], np.nan)
    yeterli = n_et >= c["min_etiket"]
    for s in ESIKLER:
        out[f"benzer_12ay_t{int(s * 100)}"] = pd.array(np.where(yeterli, benzer[s], 0), dtype="Int64")
        out.loc[~yeterli, f"benzer_12ay_t{int(s * 100)}"] = pd.NA
    k_ = o.kohort.values
    K.ekle(
        "C01",
        f"İçerik etiketi < {c['min_etiket']} (vektör güvenilmez)",
        int((~gecerli & k_).sum()),
        int(k_.sum()),
        "novelty ve benzer_12ay = NULL",
        "Az etiketle kosinüs uzaklığı anlamsız; T13",
    )

    # Tür kombinasyonu: en güçlü 2 A_tur etiketi (sırasız); yalnız 1 varsa o
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet", columns=["appid", "tagid", "sira", "ad"])
    e = e[e.tagid.isin(tx.tagid[(tx.boyut == "A_tur") & (tx.alt_grup != "ana")])].sort_values(["appid", "sira"])  # 'ana' (Action, Casual…) çok kaba
    kombo = e.groupby("appid").ad.apply(lambda v: " + ".join(sorted(v.iloc[:2])))
    out["tur_kombo"] = out.appid.map(kombo)
    kd = out[["appid", "tur_kombo"]].assign(cikis=o.cikis.values).dropna(subset=["tur_kombo"])
    sayi = np.zeros(len(kd), dtype=np.int32)
    for _, g in kd.groupby("tur_kombo"):
        tt = g.cikis.values.astype("datetime64[ns]")
        sayi[kd.index.get_indexer(g.index)] = np.searchsorted(tt, tt, side="left") - np.searchsorted(tt, tt - np.timedelta64(365, "D"), side="left")
    out["kombo_12ay"] = pd.Series(sayi, index=kd.index).reindex(out.index).astype("Int64")
    K.ekle(
        "C02",
        "Alt tür etiketi yok (tür kombinasyonu tanımsız)",
        int(out.tur_kombo.isna().values[k_].sum()),
        int(k_.sum()),
        "kombo_12ay = NULL",
        "Yalnız kaba 'ana' tür etiketi taşıyan oyunlar",
    )

    esik = c.get("benzer_esik")
    if esik is not None:
        out["benzer_12ay"] = out[f"benzer_12ay_t{int(esik * 100)}"]
    kk = out[k_]
    print("\nEn yakın komşu benzerliği (kohort) yüzdelikleri:", kk.en_yakin_benzerlik.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(3).to_dict())
    print("novelty_k10 yüzdelikleri:", kk.novelty_k10.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(3).to_dict())
    for s in ESIKLER:
        v = kk[f"benzer_12ay_t{int(s * 100)}"].astype(float)
        print(
            f"benzer_12ay (eşik {s}): ortanca {v.median():.0f} · %5 {v.quantile(0.05):.0f} · %95 {v.quantile(0.95):.0f} · sıfır payı %{(v == 0).mean() * 100:.1f}"
        )
    v = kk.kombo_12ay.astype(float)
    print(f"kombo_12ay: ortanca {v.median():.0f} · %95 {v.quantile(0.95):.0f} · farklı kombinasyon {kk.tur_kombo.nunique():,}")
    out.to_parquet(INTERIM / "icerik.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] icerik: {len(out):,} oyun")


if __name__ == "__main__":
    main()
