#!/usr/bin/env bash
# Process hattı: interim → kontroller → yayın. Çekimler (00–05) ayrı çalıştırılır (uzun sürer, kaldığı yerden devam eder).
# Kullanım (proje klasöründen): bash scripts/hat.sh
# Her adım bir öncekinin çıktısını okur; kontrol başarısızsa (12) hat durur ve yayın yapılmaz.
set -euo pipefail
cd "$(dirname "$0")"
PY=(uv run --quiet --no-project --python 3.12 --with pandas --with pyarrow --with pyyaml --with requests --with python-dotenv --with numpy --with duckdb --with openpyxl python)
for adim in 10_temizle_steam 10b_temizle_igdb 11_sonuc 10c_temizle_tur 11b_oznitelik 11d_basari r01_etiket_taksonomi 11c_icerik 12_kontrol 13_yayinla; do
  echo "== $adim"
  "${PY[@]}" "$adim.py"
done
