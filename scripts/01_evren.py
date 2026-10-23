"""01: Evren listesi ve pilot örneklemi.

Girdi : data/raw/fronkongames/*/games.parquet (en yeni sürüm)
Çıktı : data/interim/evren.parquet   — appid, ad, setteki çıkış tarihi/yılı, setteki inceleme toplamı (sadece tabaka için)
        data/interim/pilot_appid.csv  — yıl × kademe tabakalı 1.000 oyun (sabit tohum)
Not   : Setteki inceleme sayısı SONUÇ olarak kullanılmaz; yalnız pilot tabakalaması içindir.
"""

from __future__ import annotations

import pandas as pd
from ortak import INTERIM, RAW, ayarlar

TOHUM = 20261022


def main() -> None:
    cfg = ayarlar()
    kaynak = sorted((RAW / "fronkongames").glob("*/games.parquet"))[-1]
    df = pd.read_parquet(kaynak, columns=["appID", "name", "release_date", "positive", "negative"])
    df = df.rename(columns={"appID": "appid", "name": "ad_set"})
    df["appid"] = df.appid.astype("int64")
    df["cikis_set"] = pd.to_datetime(df.release_date, format="mixed", errors="coerce")
    df["yil_set"] = df.cikis_set.dt.year.astype("Int64")
    df["inceleme_set"] = df.positive + df.negative
    df["evren_kaynak"] = str(kaynak.relative_to(kaynak.parents[3]))
    evren = df[["appid", "ad_set", "cikis_set", "yil_set", "inceleme_set", "evren_kaynak"]]
    INTERIM.mkdir(parents=True, exist_ok=True)
    evren.to_parquet(INTERIM / "evren.parquet", index=False)

    bas, bit = int(str(cfg["kohort"]["baslangic"])[:4]), int(str(cfg["kohort"]["bitis"])[:4])
    k = evren[(evren.yil_set >= bas) & (evren.yil_set <= bit)].copy()
    sinirlar = [-1, *[s - 1 for s in cfg["basari"]["kademeler"]], float("inf")]  # T0..T4
    k["kademe_set"] = pd.cut(k.inceleme_set, bins=sinirlar, labels=["T0", "T1", "T2", "T3", "T4"])
    n_tabaka = k.groupby(["yil_set", "kademe_set"], observed=True).ngroups
    pay = 1000 // n_tabaka
    pilot = k.sample(frac=1, random_state=TOHUM).groupby(["yil_set", "kademe_set"], observed=True).head(pay)
    pilot[["appid", "yil_set", "kademe_set"]].to_csv(INTERIM / "pilot_appid.csv", index=False)
    print(f"evren={len(evren):,} kohort(set tarihi)={len(k):,} tabaka={n_tabaka} pilot={len(pilot)}")


if __name__ == "__main__":
    main()
