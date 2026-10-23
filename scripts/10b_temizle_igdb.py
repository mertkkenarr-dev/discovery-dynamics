"""10b: IGDB ham cevapları → appid bazlı tablolar.

Kullanım: cd scripts && python 10b_temizle_igdb.py      (05_igdb.py ve 10_temizle_steam.py'den sonra)
Çıktı   : interim/oyun_igdb.parquet          appid, igdb_id, igdb_tur, igdb_ilk_cikis, n_<alan> (alan boşsa NULL)
          interim/oyun_igdb_ozellik.parquet  appid, alan, deger_id, ad   (tür, tema, mod, bakış açısı, anahtar kelime, motor)
Eşleşme yalnızca IGDB'nin Steam kimliği üzerinden (T10). Oynama süresi (%3,5) ve stüdyo ülkesi (%15) seyrek olduğu için
alınmaz; bkz. PILOT_RAPORU 'IGDB eşleştirmesi'.
"""

from __future__ import annotations

import importlib

import pandas as pd
from ortak import INTERIM, KararKaydi

satirlar = importlib.import_module("05_igdb").satirlar

TUR_AD = {0: "ana_oyun", 1: "dlc", 2: "genisleme", 3: "paket", 4: "bagimsiz_genisleme", 5: "mod", 6: "bolum", 7: "sezon",
          8: "remake", 9: "remaster", 10: "genisletilmis", 11: "port", 12: "fork", 13: "pack", 14: "guncelleme"}  # fmt: skip
ALANLAR = {"genres": ("tur", "genres"), "themes": ("tema", "themes"), "game_modes": ("mod", "game_modes"),
           "player_perspectives": ("bakis", "player_perspectives"), "keywords": ("anahtar", "keywords"), "game_engines": ("motor", "game_engines")}  # fmt: skip


def main() -> None:
    K = KararKaydi("10b_temizle_igdb")
    oyun = pd.read_parquet(INTERIM / "oyun_steam.parquet", columns=["appid"])
    eg = pd.DataFrame(satirlar("external_games"))
    eg = eg[eg.uid.str.fullmatch(r"\d+", na=False)].assign(appid=lambda d: d.uid.astype(int))
    eg = eg[eg.appid.isin(oyun.appid)][["appid", "game"]].drop_duplicates()
    cok = eg.appid.duplicated(keep=False)
    K.ekle(
        "T10",
        "Bir appID birden fazla IGDB oyununa bağlı",
        int(cok.sum()),
        len(eg),
        "Eşleşme kullanılmaz (belirsiz)",
        "Yanlış içerik ataması riskini almak yerine eksik bırakılır",
    )
    eg = eg[~cok]

    g = pd.DataFrame(satirlar("games")).rename(columns={"id": "game"})
    m = eg.merge(g, on="game", how="left")
    donmeyen = m.name.isna()
    K.ekle("T10b", "Steam bağlantısı var ama IGDB oyun kaydı dönmedi", int(donmeyen.sum()), len(m), "Eşleşmesiz sayılır", "Kayıt silinmiş ya da gizli")
    m = m[~donmeyen]
    paylasan = m.game.duplicated(keep=False)
    K.ekle(
        "T10c",
        "Aynı IGDB oyunu birden fazla appID'ye bağlı (aynı oyunun farklı Steam sürümleri)",
        int(paylasan.sum()),
        len(m),
        "Nitelikler her appID'ye kopyalanır; igdb_paylasimli bayrağı",
        "Remaster / sürüm farkı; içerik aynı",
    )

    o = pd.DataFrame(
        {
            "appid": m.appid,
            "igdb_id": m.game.astype(int),
            "igdb_tur": m.game_type.map(TUR_AD),
            "igdb_ilk_cikis": pd.to_datetime(m.first_release_date, unit="s"),
            "igdb_paylasimli": paylasan.values,
        }
    )
    uzun = []
    for alan, (kisa, uc) in ALANLAR.items():
        ad = {r["id"]: r.get("name") for r in satirlar(uc)}
        dolu = m[alan].notna()
        o[f"n_{kisa}"] = m[alan].map(lambda v: len(v) if isinstance(v, list) else None).astype("Int64").values  # boş alan = NULL (T13)
        ex = m.loc[dolu, ["appid", alan]].explode(alan)
        uzun.append(pd.DataFrame({"appid": ex.appid, "alan": kisa, "deger_id": ex[alan].astype(int), "ad": ex[alan].map(ad)}))
        print(f"      {kisa:8s}: dolu %{dolu.mean() * 100:5.1f}  farklı değer {ex[alan].nunique():,}")
    oz = pd.concat(uzun, ignore_index=True)
    # Sızıntı (R6): çıkıştan SONRA oluşan anahtar kelimeler. Kesin desenler; elle kontrol edildi (2026-10-23).
    # Kickstarter, twitch entegrasyonu gibi çıkış ÖNCESİ bilgiler sızıntı değildir ve tutulur.
    # İstisna: "world premiere" çıkış öncesi tanıtımdır, "avatar awards" eski bir Xbox özelliğidir; ikisi de sızıntı değil.
    sonradan = r"(?:award|nominee|winner|game critics|golden joystick|bafta|\bgoty\b|game of the year|netflix|playstation plus|game pass|^free game$|giveaway)"
    istisna = r"(?:world premiere|avatar awards)"
    ad = oz.ad.fillna("")
    oz["sonradan_bilgi"] = (oz.alan == "anahtar") & ad.str.contains(sonradan, case=False, regex=True) & ~ad.str.contains(istisna, case=False, regex=True)
    K.ekle(
        "T10e",
        f"IGDB anahtar kelimesi çıkıştan sonra oluşan bilgi (ödül, Netflix/PS Plus/Game Pass, bedava dağıtım): {oz[oz.sonradan_bilgi].ad.nunique()} farklı kelime",
        int(oz.sonradan_bilgi.sum()),
        int((oz.alan == "anahtar").sum()),
        "sonradan_bilgi bayrağı; tahmin modeline hiçbir anahtar kelime girmez, betimsel analizde bunlar çıkarılır",
        "Başarının sonucu olan bilgi neden gibi görünür (ör. Hades: 'The Game Awards - best action game - winner')",
    )
    adsiz = oz.ad.isna()
    K.ekle(
        "T10d",
        "Sözlükte adı bulunmayan IGDB kimliği",
        int(adsiz.sum()),
        len(oz),
        "Kimlik tutulur, ad NULL",
        "Sözlük çekimi kimliği döndürmedi; analiz kimlikle yapılır",
    )

    o.to_parquet(INTERIM / "oyun_igdb.parquet", index=False)
    oz.to_parquet(INTERIM / "oyun_igdb_ozellik.parquet", index=False)
    K.kaydet()
    print(f"\n[ok] oyun_igdb: {len(o):,} appID · özellik satırı {len(oz):,}")


if __name__ == "__main__":
    main()
