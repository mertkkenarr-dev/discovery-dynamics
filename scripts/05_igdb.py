"""05: IGDB → içerik zenginleştirme (tema, oyun modu, bakış açısı, motor, anahtar kelime, oynama süresi, stüdyo ülkesi).

Eşleştirme (T10): sadece IGDB `external_games` tablosundaki Steam kimliği (external_game_source = 1) ile; ad üzerinden
eşleştirme yapılmaz. Eski `category` alanı 2025'te kaldırıldı, bu yüzden `external_game_source` kullanılır.

Kullanım: python 05_igdb.py [--adim eslesme|oyunlar|ttb|sirket|sozluk|hepsi]
Çıktı   : data/raw/igdb/<uç nokta>.jsonl.gz. Her satır bir parti: {"_istenen": [...], "sonuc": [...], "_fetched_at"}.
          Karşılığı olmayan kimlikler de "_istenen" içinde kalır; devam ederken tekrar sorulmaz.
Gerekli : .env içinde TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET.
"""

from __future__ import annotations

import argparse
import os
import time

import requests
from dotenv import load_dotenv
from ortak import KOK, RAW, Hiz, ayarlar, jsonl_gz_ekle, jsonl_gz_oku, simdi_utc

DIZIN = RAW / "igdb"
API = "https://api.igdb.com/v4/"
PARTI = 500  # IGDB'nin istek başına üst sınırı
STEAM = 1

OYUN_ALANLARI = (
    "name,slug,game_type,first_release_date,genres,themes,game_modes,player_perspectives,keywords,game_engines,"
    "involved_companies,franchises,collections,parent_game,version_parent,total_rating_count"
)
SOZLUK = {
    "genres": "genres",
    "themes": "themes",
    "game_modes": "game_modes",
    "player_perspectives": "player_perspectives",
    "keywords": "keywords",
    "game_engines": "game_engines",
}  # games alanı → uç nokta


class Igdb:
    def __init__(self) -> None:
        load_dotenv(KOK / ".env")
        self.cid, sec = os.environ["TWITCH_CLIENT_ID"], os.environ["TWITCH_CLIENT_SECRET"]
        r = requests.post(
            "https://id.twitch.tv/oauth2/token", params={"client_id": self.cid, "client_secret": sec, "grant_type": "client_credentials"}, timeout=30
        )
        r.raise_for_status()
        self.oturum = requests.Session()
        self.oturum.headers.update({"Client-ID": self.cid, "Authorization": "Bearer " + r.json()["access_token"]})
        self.hiz = Hiz(ayarlar()["hiz_limiti_saniye"]["igdb"])

    def sorgu(self, uc: str, govde: str, deneme: int = 6) -> list[dict]:
        for i in range(deneme):
            self.hiz.bekle()
            try:
                r = self.oturum.post(API + uc, data=govde, timeout=60)
            except requests.RequestException:
                time.sleep(2 * 2**i)
                continue
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 * 2**i)
                continue
            raise RuntimeError(f"IGDB {uc} {r.status_code}: {r.text[:300]}")
        raise RuntimeError(f"IGDB kalıcı hata: {uc}")


def satirlar(uc: str):
    for p in jsonl_gz_oku(DIZIN / f"{uc}.jsonl.gz"):
        yield from p["sonuc"]


def kimlige_gore(api: Igdb, uc: str, alanlar: str, anahtar: str, kimlikler: set[int]) -> None:
    """Kimlik listesini 500'lük partilerle çeker; daha önce sorulanları atlar."""
    yol = DIZIN / f"{uc}.jsonl.gz"
    sorulan = {i for p in jsonl_gz_oku(yol) for i in p["_istenen"]}
    kalan = sorted(kimlikler - sorulan)
    print(f"[{uc}] istenecek {len(kalan):,} (önceden sorulan {len(sorulan):,})", flush=True)
    for b in range(0, len(kalan), PARTI):
        parca = kalan[b : b + PARTI]
        sonuc = api.sorgu(uc, f"fields {alanlar}; where {anahtar} = ({','.join(map(str, parca))}); limit {PARTI};")
        jsonl_gz_ekle(yol, [{"_istenen": parca, "sonuc": sonuc, "_fetched_at": simdi_utc()}])
        if (b // PARTI) % 20 == 0:
            print(f"  {b + len(parca):,}/{len(kalan):,}", flush=True)


def eslesme(api: Igdb) -> None:
    """Steam bağlantılarının tamamı; id sırasıyla anahtar tabanlı sayfalama (offset sınırına takılmaz)."""
    yol = DIZIN / "external_games.jsonl.gz"
    son = max((r["id"] for r in satirlar("external_games")), default=0)
    toplam = api.sorgu("external_games/count", f"where external_game_source = {STEAM};")
    print(f"[external_games] IGDB'deki Steam bağlantısı: {toplam}; kaldığı id: {son}", flush=True)
    while True:
        sonuc = api.sorgu(
            "external_games", f"fields id,game,uid,name,external_game_source; where external_game_source = {STEAM} & id > {son}; sort id asc; limit {PARTI};"
        )
        if not sonuc:
            break
        jsonl_gz_ekle(yol, [{"_istenen": [son], "sonuc": sonuc, "_fetched_at": simdi_utc()}])
        son = sonuc[-1]["id"]
    print(f"  bitti; satır: {sum(1 for _ in satirlar('external_games')):,}")


def hedef_oyunlar() -> set[int]:
    """Evrendeki Steam oyunlarına (GetItems type=0) karşılık gelen IGDB oyun kimlikleri."""
    oyun_appid = {x["_istenen_appid"] for x in jsonl_gz_oku(RAW / "steam_getitems" / "items.jsonl.gz") if x.get("success") == 1 and x.get("type") == 0}
    return {r["game"] for r in satirlar("external_games") if r.get("uid", "").isdigit() and int(r["uid"]) in oyun_appid and r.get("game")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adim", default="hepsi", choices=["eslesme", "oyunlar", "ttb", "sirket", "sozluk", "hepsi"])
    a = ap.parse_args()
    api = Igdb()
    hepsi = a.adim == "hepsi"
    if hepsi or a.adim == "eslesme":
        eslesme(api)
    if hepsi or a.adim == "oyunlar":
        kimlige_gore(api, "games", OYUN_ALANLARI, "id", hedef_oyunlar())
    oyunlar = list(satirlar("games"))
    if hepsi or a.adim == "ttb":
        kimlige_gore(api, "game_time_to_beats", "game_id,hastily,normally,completely,count", "game_id", {g["id"] for g in oyunlar})
    if hepsi or a.adim == "sirket":
        kimlige_gore(
            api,
            "involved_companies",
            "game,company,developer,publisher,porting,supporting",
            "id",
            {i for g in oyunlar for i in g.get("involved_companies", [])},
        )
        sirketler = {r["company"] for r in satirlar("involved_companies") if r.get("company")}
        kimlige_gore(api, "companies", "name,slug,country,start_date,parent", "id", sirketler)
    if hepsi or a.adim == "sozluk":
        for alan, uc in SOZLUK.items():
            kimlige_gore(api, uc, "name,slug", "id", {i for g in oyunlar for i in g.get(alan, [])})
    print("[ok]")


if __name__ == "__main__":
    main()
