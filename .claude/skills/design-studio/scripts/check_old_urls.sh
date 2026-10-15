#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Every URL the pre-restructure site published (references/old-urls.txt,
# from its sitemap) must still answer on the live server — as a page or an
# alias redirect. Retired on purpose: /posts/, /tags/, /categories/,
# /sections/ (empty theme-skeleton pages).
#
# Usage: check_old_urls.sh [BASE_URL]   (default: the serve.sh URL)
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="${1:-$(bash "$DIR/serve.sh")}"
BASE="${BASE%/}"
fail=0
while read -r path; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$path")
  if [[ "$code" != 200 ]]; then echo "FAIL $code $path"; fail=1; fi
done < "$DIR/../references/old-urls.txt"
[[ $fail -eq 0 ]] && echo "check_old_urls: all $(wc -l < "$DIR/../references/old-urls.txt") old URLs resolve"
exit $fail
