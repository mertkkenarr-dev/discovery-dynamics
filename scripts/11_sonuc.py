"""11: Sonuç metrikleri — inceleme grafiğinden (appreviewhistogram) reviews_30/90/365, olumlu oran, tail_share, kademe, hit.

Kullanım: cd scripts && python 11_sonuc.py          (10_temizle_steam.py'den sonra)
Girdi   : raw/steam_histogram/histogram.jsonl.gz, interim/oyun_steam.parquet
Çıktı   : interim/sonuc.parquet         oyun başına sonuçlar (kohort oyunları)
          interim/inceleme_seri.parquet appid × kova (M4 yörüngeleri için uzun tablo)

Pencere hesabı: kovalar aylık (eski oyunlar) ya da haftalık. Çıkışın düştüğü kova çıkış gününden başlatılır (çıkıştan
önce inceleme olmaz); pencere sınırındaki kova gün oranıyla bölünür. Aylık kovalarda reviews_30/90 yaklaşıktır,
reviews_365'te hata küçüktür (sınır kovası geç kuyruğa düşer). Bkz. PILOT_RAPORU 'Sonuç metrikleri'.
Hipotez testi YOK.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from ortak import INTERIM, RAW, KararKaydi, ayarlar, jsonl_gz_oku

GUN = pd.Timedelta(days=1)
ONCEDEN_ESIK = 10  # T14: çıkış ayından önceki inceleme sayısı bu değere ulaşırsa tarih düzeltilir


def kovalar(res: dict) -> pd.DataFrame:
    r = pd.DataFrame(res.get("rollups") or [])
    if r.empty:
        return r
    r["bas"] = pd.to_datetime(r.date, unit="s")
    adim = pd.DateOffset(months=1) if res.get("rollup_type") == "month" else pd.Timedelta(days=7)
    r["son"] = r.bas + adim
    return r.rename(columns={"recommendations_up": "up", "recommendations_down": "down"})[["bas", "son", "up", "down"]]


def pencere(k: pd.DataFrame, t0: pd.Timestamp, gun: int) -> tuple[float, float]:
    """[t0, t0+gun) penceresine düşen olumlu/olumsuz; kovalar t0'dan önce başlıyorsa t0'dan kırpılır."""
    t1 = t0 + gun * GUN
    bas = k.bas.where(k.bas > t0, t0)
    uzun = (k.son - bas).dt.total_seconds()
    ortak = ((k.son.where(k.son < t1, t1)) - bas).dt.total_seconds().clip(lower=0)
    pay = np.where(uzun > 0, ortak / uzun, 0.0)
    pay = np.where(k.son <= t0, 0.0, pay)
    return float((k.up * pay).sum()), float((k.down * pay).sum())


def main() -> None:
    cfg, K = ayarlar(), KararKaydi("11_sonuc")
    o = pd.read_parquet(INTERIM / "oyun_steam.parquet")
    # Kohort sonrası tarihli oyunlar da işlenir: T14 düzeltmesiyle gerçek tarihleri kohorta düşebilir; kohort aşağıda yeniden belirlenir
    o = o[o.ilk_cikis >= pd.Timestamp(str(cfg["kohort"]["baslangic"]))].set_index("appid")
    hit, kademe = cfg["basari"]["hit_esik"], cfg["basari"]["kademeler"]
    rows, seri = [], []
    for x in jsonl_gz_oku(RAW / "steam_histogram" / "histogram.jsonl.gz"):
        a = x["appid"]
        if a not in o.index or x.get("success") != 1:
            continue
        res, t0 = x["results"], o.at[a, "ilk_cikis"]
        k = kovalar(res)
        if k.empty:
            continue
        seri.append(k.assign(appid=a))
        t0_kova = k.bas[k.bas <= t0].max() if (k.bas <= t0).any() else k.bas.min()
        onceki = int(k.loc[k.bas < t0_kova, ["up", "down"]].sum().sum())
        kaynak = "steam"
        if onceki >= ONCEDEN_ESIK:  # T14: Steam yeniden yayında / kayıtsız EA'da tarihi sıfırlıyor → ilk inceleme günü
            t0, kaynak = pd.to_datetime(res["start_date"], unit="s"), "ilk_inceleme"
        son_kova = k.bas.max()
        d = {
            "appid": a,
            "ilk_cikis": t0,
            "ilk_cikis_kaynagi": kaynak,
            "cozunurluk": res.get("rollup_type"),
            "omur_hist": int(k.up.sum() + k.down.sum()),
            "onceden_inceleme": onceki,
        }
        for g in (30, 90, 365):
            up, dn = pencere(k, t0, g)
            tamam = t0 + g * GUN <= son_kova  # sınır kovası tam gözlenmiş olmalı (R2)
            d[f"reviews_{g}"] = up + dn if tamam else np.nan
            if g == 365:
                d["olumlu_oran_365"] = up / (up + dn) if tamam and up + dn > 0 else np.nan
        rows.append(d)
    s = pd.DataFrame(rows).set_index("appid")
    print(f"Histogramı olan oyun (ilk erişim ≥ kohort başı): {len(s):,} / {len(o):,}\n")

    # < 10 inceleme: histogram çekilmedi; T0 ve hit=0 kesin, sürekli değer = ömür boyu üst sınır
    az = o.index[(o.inceleme_omur < 10) & ~o.index.isin(s.index)]
    gozlem = o.gozlem_gun >= 365 + 31
    a_ = pd.DataFrame(index=az).assign(
        ilk_cikis=o.loc[az, "ilk_cikis"],
        ilk_cikis_kaynagi="steam",
        cozunurluk="yok",
        omur_hist=np.nan,
        onceden_inceleme=np.nan,
        reviews_30=np.nan,
        reviews_90=np.nan,
    )
    a_["reviews_365"] = o.loc[az, "inceleme_omur"].where(gozlem.loc[az]).astype(float)
    s["sonuc_kaynagi"], a_["sonuc_kaynagi"] = "histogram", "omur_ust_sinir"
    K.ekle(
        "S01",
        "Ömür boyu < 10 inceleme: histogram çekilmedi",
        len(az),
        len(o),
        "reviews_365 = ömür boyu sayı (üst sınır), sadece ≥ 396 gün gözlenenlerde",
        "reviews_365 ≤ ömür boyu < 10 → kademe T0 ve hit=0 kesin; sürekli değerde hata < 10",
    )
    eksik = o.index[(o.inceleme_omur >= 10) & ~o.index.isin(s.index)]
    K.ekle(
        "S02",
        "≥ 10 inceleme ama histogram yok (çekim eksik / boş cevap)",
        len(eksik),
        len(o),
        "Sonuç NULL; tamamlanınca 03_histogram.py tekrar çalıştırılır",
        "Eksik veri sıfır sayılmaz (T13)",
    )
    s = pd.concat([s, a_])
    s = s.join(o[["inceleme_omur", "fetched_at"]])
    s["gozlem_gun"] = (s.fetched_at - s.ilk_cikis).dt.days
    bas, bit = pd.Timestamp(str(cfg["kohort"]["baslangic"])), pd.Timestamp(str(cfg["kohort"]["bitis"])) + GUN
    s["kohort"] = (s.ilk_cikis >= bas) & (s.ilk_cikis < bit)

    K.ekle(
        "S03",
        "365 gün penceresi tam gözlenmemiş (sağdan sansür, R2)",
        int(s.reviews_365.isna().sum()),
        len(s),
        "reviews_365, kademe ve hit = NULL",
        "Kısa gözlenen oyunlar haksız yere 'başarısız' görünmesin",
    )

    h = s.sonuc_kaynagi == "histogram"
    s["r12_oran"] = (s.omur_hist / s.inceleme_omur).where(h & (s.inceleme_omur > 0))
    r12 = s.r12_oran.between(0.95, 1.30)
    print("      R12 oran yüzdelikleri:", s.r12_oran.quantile([0.01, 0.1, 0.5, 0.9, 0.99]).round(3).to_dict())
    K.ekle(
        "S04",
        "R12: histogram ömür toplamı ÷ GetItems özeti 0,95–1,30 dışında",
        int((h & ~r12).sum()),
        int(h.sum()),
        "r12_uyumsuz bayrağı; ana analizde tutulur, duyarlılıkta çıkarılır",
        "Kaynaklar arası tutarsızlık sessiz çekim hatasına işaret edebilir",
    )
    s["r12_uyumsuz"] = h & ~r12

    duz = s.ilk_cikis_kaynagi == "ilk_inceleme"
    K.ekle(
        "T14",
        f"Steam çıkış ayından önce ≥ {ONCEDEN_ESIK} inceleme (yeniden yayında sıfırlanan tarih / kayıtsız EA); {int((duz & ~s.kohort).sum()):,} tanesi gerçekte 2018 öncesi",
        int(duz.sum()),
        int(h.sum()),
        "ilk_cikis = ilk inceleme günü (histogram start_date); pencereler ve kohort yeni tarihle hesaplanır; 2018 öncesine düşenler kohort=False",
        "İncelemeler oyunun gerçekte ne zamandan beri satıldığını gösterir (Rust, GTA IV, Satisfactory); normal oyunlarda iki tarih farkı ortanca −1 gün",
    )

    s["tail_share"] = ((s.reviews_365 - s.reviews_90) / s.reviews_365).where(s.reviews_365 > 0)
    r365 = s.reviews_365.round()  # sınır kovası kesirli pay verir; 499,6 → 500
    s["kademe"] = pd.cut(r365, [-np.inf, *[v - 0.5 for v in kademe], np.inf], labels=[f"T{i}" for i in range(len(kademe) + 1)])
    s["hit"] = (r365 >= hit).astype("boolean").where(s.reviews_365.notna())
    s.reset_index(names="appid").to_parquet(INTERIM / "sonuc.parquet", index=False)
    pd.concat(seri, ignore_index=True).to_parquet(INTERIM / "inceleme_seri.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] sonuc: {len(s):,} satır · reviews_365 dolu {s.reviews_365.notna().sum():,} · seri satırı {sum(map(len, seri)):,}")


if __name__ == "__main__":
    main()
