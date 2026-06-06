#!/bin/bash
mkdir -p results
GROUP_SUFFIX=$1

split -d -n l/4 targets.txt targets_group
TARGET_FILE="targets_group${GROUP_SUFFIX}"

scan_sf() {
    local domain=$(echo "$1" | xargs)
    [[ -z "$domain" || "$domain" =~ ^# ]] && return

    echo "[+] [$domain] [SecretFinder Matrix Worker] Discovering JS targets..."
    echo "$domain" | gau 2>/dev/null | grep -E '\.js($|\?)' 2>/dev/null | head -n 100 > "results/${domain}_js_temp.txt"

    if [ -s "results/${domain}_js_temp.txt" ]; then
        echo "[+] [$domain] [SecretFinder Matrix Worker] Parsing 100 JS files in parallel..."
        xargs -P 2 -I {} sh -c 'python SecretFinder/SecretFinder.py -i "{}" -o cli 2>/dev/null' < "results/${domain}_js_temp.txt" > "results/${domain}_secretfinder.txt"
    else
        echo "  -> [$domain] No JS assets found."
    fi
    rm -f "results/${domain}_js_temp.txt"
}

export -f scan_sf
echo "[*] Starting Dynamic Matrix SecretFinder Scanner for $TARGET_FILE..."
xargs -P 10 -n 1 -a "$TARGET_FILE" -I {} bash -c 'scan_sf "{}"'

rm -f targets_group*
