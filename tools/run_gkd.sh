#!/bin/sh
# Second game uses distinct names; it never overwrites Detective_Kent.
launcher_dir=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd) || exit 1
game_dir="$launcher_dir/Detective_Kent2"
launcher_log="$launcher_dir/detective_kent2_launch.log"
if (umask 077; : > "$launcher_log") 2>/dev/null; then
    exec > "$launcher_log" 2>&1
fi
printf '%s\n' 'Detective Kent 2 - GKD Pixel 2'
date
game_python=${DETECTIVE_KENT2_PYTHON:-/storage/pyxel_Python/bin/python3}
if [ ! -x "$game_python" ]; then
    printf 'Python executable not found: %s\n' "$game_python" >&2
    exit 1
fi
cd "$game_dir" || exit 1
"$game_python" -c 'import sys,pyxel; print(sys.version); print("Pyxel",pyxel.VERSION)' || exit 1
exec "$game_python" -B -u main.py --gkd "$@"
