#!/usr/bin/env bash
# Adım 7: İnceleme geçmişi (appreviewhistogram) — Mac'te Terminal'den çalıştırılır.
# Kaldığı yerden devam eder: kesilirse aynı komutu tekrar çalıştırmak yeterli.
# Kullanım (proje klasöründen):  caffeinate -i bash scripts/calistir_histogram.sh
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v uv >/dev/null 2>&1; then
  echo "uv bulunamadı. Kurmak için:  brew install uv   (ya da: curl -LsSf https://astral.sh/uv/install.sh | sh)"
  exit 1
fi
uv run --quiet --no-project --python 3.12 \
  --with pandas --with pyarrow --with pyyaml --with requests \
  python 03_histogram.py --liste evren --paralel 4 --min-inceleme 10
echo "Bitti. Claude'a 'bitti' yazabilirsin."
