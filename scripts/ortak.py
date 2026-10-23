"""Ortak yardımcılar: yollar, ayarlar, ham veri manifestosu."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

KOK = Path(__file__).resolve().parents[1]
RAW = KOK / "data" / "raw"
INTERIM = KOK / "data" / "interim"
PROCESSED = KOK / "data" / "processed"
MANIFEST = RAW / "_manifest.csv"
MANIFEST_ALANLAR = ["kaynak", "dosya", "url", "cekim_utc", "bayt", "sha256", "lisans", "not"]


def ayarlar() -> dict:
    return yaml.safe_load((KOK / "config.yaml").read_text(encoding="utf-8"))


def simdi_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(yol: Path, blok: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with yol.open("rb") as f:
        while chunk := f.read(blok):
            h.update(chunk)
    return h.hexdigest()


def manifeste_ekle(kaynak: str, dosya: Path, url: str, lisans: str, not_: str = "") -> None:
    """Ham dosyayı manifestoya işler; aynı sha256 zaten kayıtlıysa tekrar yazmaz."""
    RAW.mkdir(parents=True, exist_ok=True)
    ozet = sha256(dosya)
    mevcut = []
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8") as f:
            mevcut = list(csv.DictReader(f))
        if any(r["sha256"] == ozet for r in mevcut):
            return
    yeni = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_ALANLAR)
        if yeni:
            w.writeheader()
        w.writerow(
            {
                "kaynak": kaynak,
                "dosya": str(dosya.relative_to(KOK)),
                "url": url,
                "cekim_utc": simdi_utc(),
                "bayt": dosya.stat().st_size,
                "sha256": ozet,
                "lisans": lisans,
                "not": not_,
            }
        )


# --- HTTP ---------------------------------------------------------------------------------------
import gzip  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402

import requests  # noqa: E402

OTURUM = requests.Session()
OTURUM.headers["User-Agent"] = "discovery-dynamics/0.1 (portfolio research; non-commercial)"


def http_json(url: str, params: dict | None = None, deneme: int = 6, bekle: float = 2.0) -> dict | None:
    """GET + JSON. 429/5xx ve ağ hatalarında üstel geri çekilmeyle tekrar dener; 4xx (429 hariç) → None."""
    for i in range(deneme):
        try:
            r = OTURUM.get(url, params=params, timeout=45)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(bekle * 2**i)
                continue
            return None
        except (requests.RequestException, ValueError):
            time.sleep(bekle * 2**i)
    raise RuntimeError(f"Kalıcı hata: {url}")


class Hiz:
    """Kaynak başına sabit istek aralığı."""

    def __init__(self, saniye: float):
        self.saniye, self.son = saniye, 0.0

    def bekle(self) -> None:
        kalan = self.saniye - (time.monotonic() - self.son)
        if kalan > 0:
            time.sleep(kalan)
        self.son = time.monotonic()


def jsonl_gz_oku(yol: Path):
    if not yol.exists():
        return
    with gzip.open(yol, "rt", encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                yield json.loads(satir)


def jsonl_gz_ekle(yol: Path, kayitlar: list[dict]) -> None:
    yol.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(yol, "at", encoding="utf-8") as f:
        for k in kayitlar:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")


# --- Tanımlar -----------------------------------------------------------------------------------
def ilk_steam_erisimi(item: dict) -> int | None:
    """Oyunun Steam'de ilk satın alınabilir olduğu an (unix sn): min(steam_release_date, original_steam_release_date).

    GetItems'ta steam_release_date EA'dan çıkmış oyunlarda TAM SÜRÜM tarihidir; EA başlangıcı
    original_steam_release_date'tedir (Slay the Spire, Hades, Vampire Survivors ile doğrulandı). Kohort ve
    reviews_365'in sıfır noktası bu fonksiyondan gelir. 1990 öncesi değerler (boş zaman damgası) geçersiz sayılır.
    """
    r = item.get("release") or {}
    adaylar = [t for t in (r.get("steam_release_date"), r.get("original_steam_release_date")) if t and t >= 631152000]
    return min(adaylar) if adaylar else None


class KararKaydi:
    """Temizlik kararları: sorun → etkilenen kayıt → karar → gerekçe. Hem ekrana basılır hem meta_karar'a yazılır."""

    def __init__(self, betik: str):
        self.betik, self.satirlar = betik, []

    def ekle(self, kod: str, sorun: str, etkilenen: int, toplam: int, karar: str, gerekce: str) -> None:
        self.satirlar.append({"kod": kod, "betik": self.betik, "sorun": sorun, "etkilenen": etkilenen, "toplam": toplam, "karar": karar, "gerekce": gerekce})
        print(f"[{kod}] {sorun}\n      etkilenen: {etkilenen:,} / {toplam:,} (%{etkilenen / max(toplam, 1) * 100:.1f})\n      karar    : {karar}\n      gerekçe  : {gerekce}", flush=True)

    def kaydet(self) -> None:
        import pandas as pd

        yol = INTERIM / "meta_karar.parquet"
        eski = pd.read_parquet(yol) if yol.exists() else pd.DataFrame()
        if len(eski):
            eski = eski[eski.betik != self.betik]  # betik yeniden çalışınca kendi eski kararlarını değiştirir
        pd.concat([eski, pd.DataFrame(self.satirlar)], ignore_index=True).to_parquet(yol, index=False)
