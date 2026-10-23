"""10c: Geliştiricinin seçtiği Steam türleri (appdetails 'genres', FronkonGames anlık görüntüsü) → interim/oyun_steam_tur.parquet,
interim/oyun_tur_ozet.parquet (appid, n_steam_tur, yazilim_suphe).

Kullanım: cd scripts && python 10c_temizle_tur.py     (10, 11_sonuc ve r01_etiket_taksonomi.py'den sonra)
Neden ayrı: kullanıcı etiketleri sonradan oylanır (R4); türleri geliştirici seçer, bu yüzden tahmin modeline yalnız bunlar girer.
Sınır: FronkonGames 2026-10-15 anlık görüntüsü; geliştirici türü sonradan değiştirmiş olabilir (çıkış anındaki değer değil).
Ek: yazılım türü/etiketi taşıyan type=0 kayıtlar 'yazilim_suphe' olarak işaretlenir (T01'i tamamlar).
"""

from __future__ import annotations

import pandas as pd
from ortak import INTERIM, KOK, RAW, KararKaydi

YAZILIM_TUR = {"Utilities", "Design & Illustration", "Animation & Modeling", "Software Training", "Audio Production", "Video Production",
               "Photo Editing", "Web Publishing", "Accounting"}  # fmt: skip
# "Game Development" bilinçli olarak dışarıda: geliştiriciler bunu "bağımsız yapım" anlamında oyunlarda da seçiyor (elle kontrol, 2026-10-23)
META_TUR = {"Indie", "Early Access", "Free to Play", "Free To Play", "Massively Multiplayer"}


def main() -> None:
    K = KararKaydi("10c_temizle_tur")
    o = pd.read_parquet(INTERIM / "oyun_steam.parquet", columns=["appid"])
    s = pd.read_parquet(INTERIM / "sonuc.parquet", columns=["appid", "kohort"])  # düzeltilmiş kohort (T14)
    o = o.merge(s, on="appid", how="left").assign(kohort=lambda d: d.kohort.fillna(False).astype(bool))
    f = pd.read_parquet(RAW / "fronkongames" / "2026-10-15" / "games.parquet", columns=["appID", "genres"])
    f["appid"] = pd.to_numeric(f.appID, errors="coerce").astype("Int64")
    f = f.dropna(subset=["appid"]).drop_duplicates("appid")
    t = f[f.appid.isin(o.appid)].explode("genres").dropna(subset=["genres"]).rename(columns={"genres": "tur"})[["appid", "tur"]]
    t["tur"] = t.tur.str.strip()
    t = t[t.tur != ""].drop_duplicates()
    t["meta"] = t.tur.isin(META_TUR)
    t["yazilim"] = t.tur.isin(YAZILIM_TUR)
    k = set(o.appid[o.kohort])
    turlu = set(t.appid)
    K.ekle(
        "T18",
        "Steam türü yok (FronkonGames'te boş ya da kayıt yok)",
        len(k - turlu),
        len(k),
        "Tür köprüsünde satırı olmaz; analizde 'tür bilinmiyor'",
        "T13: veri yok ≠ türsüz",
    )

    # T01'i tamamlayan kontrol: yalnız yazılım türü taşıyan ya da (yazılım türü + en güçlü etiketi yazılım) type=0 kayıtlar
    oyun_turu = t[~t.meta & ~t.yazilim].groupby("appid").size()
    yazilim_tur = t[t.yazilim].groupby("appid").size()
    sadece_yazilim = set(yazilim_tur.index) - set(oyun_turu.index)
    tx = pd.read_csv(KOK / "data" / "referans" / "etiket_taksonomi.csv")
    e = pd.read_parquet(INTERIM / "oyun_etiket.parquet").merge(tx[["tagid", "boyut"]], on="tagid")
    ilk_yazilim = set(e[(e.sira == 1) & (e.boyut == "X_uygulama")].appid)  # en güçlü etiket yazılımsa
    supheli = sadece_yazilim | (ilk_yazilim & set(yazilim_tur.index))
    ozet = o[["appid"]].assign(
        n_steam_tur=lambda d: d.appid.map(oyun_turu).fillna(0).astype(int),
        yazilim_suphe=lambda d: d.appid.isin(supheli),
    )
    ozet.to_parquet(INTERIM / "oyun_tur_ozet.parquet", index=False)  # her betik yalnız kendi çıktısını yazar
    K.ekle(
        "T01b",
        "type=0 ama oyun dışı yazılım işareti (yalnız yazılım türü, ya da yazılım türü + en güçlü etiket yazılım)",
        len(supheli & k),
        len(k),
        "yazilim_suphe bayrağı; ana analizden çıkarılır, duyarlılıkta dahil",
        "Steam bu kayıtları 'oyun' sınıflandırıyor ama içerik araç/yazılım; görünmez oyun oranını şişirir (R1)",
    )
    t.to_parquet(INTERIM / "oyun_steam_tur.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] oyun_steam_tur: {len(t):,} satır · {t.tur.nunique()} tür · kohortta türlü oyun %{len(turlu & k) / len(k) * 100:.1f}")
    print("Kohortta türler:", t[t.appid.isin(k)].tur.value_counts().to_dict())


if __name__ == "__main__":
    main()
