#!/usr/bin/env bash
# Render the responsive-CSS series with ManimGL and stitch each video's
# chapter scenes into one MP4 in exports/.
#
#   ./render.sh            # all three videos at 1080p
#   ./render.sh 2          # just video 2
#   ./render.sh 3 -m       # video 3 at 720p (-l = 480p, --hd = 1080p, --uhd = 4K)
#   RESUME=1 ./render.sh 1 # keep chapters already rendered in build/, render the rest
#
# Needs manimgl, ffmpeg, a LaTeX install with dvisvgm, and the Inter and
# DejaVu Sans Mono fonts. On a headless machine it runs ManimGL under xvfb-run.
set -euo pipefail
cd "$(dirname "$0")"

which="${1:-all}"
quality="${2:---hd}"

declare -A FILE=(
  [1]=scenes/video1_device_breakpoints.py
  [2]=scenes/video2_content_breakpoints.py
  [3]=scenes/video3_em_breakpoints.py
)
declare -A OUT=(
  [1]=exports/01-device-breakpoints-are-doomed.mp4
  [2]=exports/02-content-driven-breakpoints.mp4
  [3]=exports/03-em-media-queries.mp4
)

run() {
  if [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
    xvfb-run -a -s "-screen 0 1920x1080x24" "$@"
  else
    "$@"
  fi
}

videos=(1 2 3)
[ "$which" != "all" ] && videos=("$which")

mkdir -p exports build
for v in "${videos[@]}"; do
  file="${FILE[$v]}"
  dir="build/v$v"
  list="build/v$v-chapters.txt"
  mkdir -p "$dir"
  : > "$list"
  # chapters are the V<n>S<k>_* classes, in file order
  for scene in $(grep -oP "^class \KV${v}S\d+_\w+" "$file"); do
    if [ -n "${RESUME:-}" ] && [ -f "$dir/$scene.mp4" ]; then
      echo ">> video $v · $scene (kept)"
      echo "file '$PWD/$dir/$scene.mp4'" >> "$list"
      continue
    fi
    echo ">> video $v · $scene"
    run manimgl "$file" "$scene" -w "$quality" --video_dir "$dir" > "$dir/$scene.log" 2>&1 \
      || { echo "render failed, see $dir/$scene.log"; tail -20 "$dir/$scene.log"; exit 1; }
    echo "file '$PWD/$dir/$scene.mp4'" >> "$list"
  done
  ffmpeg -v error -y -f concat -safe 0 -i "$list" -c copy -movflags +faststart "${OUT[$v]}"
  echo "== ${OUT[$v]} ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "${OUT[$v]}") s)"
done
