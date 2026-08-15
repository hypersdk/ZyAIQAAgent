#!/usr/bin/env bash
# Copyright 2026 ZyvorAI Labs Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Build the ZyAIQAAgent "15-minute KT" tutorial from Playwright recordings
# (seg01..seg09) + title/caption cards (render-cards.mjs).
#
# Usage:
#   node render-cards.mjs
#   node seg01-login.mjs ... node seg09-noc.mjs   # -> raw/segNN-*/​*.webm
#   ./build.sh                                     # -> out/zyaiqaagent-kt-tutorial.mp4
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

W=1920
H=1080
FPS=30
CRF=18
PRESET=slow
FADE=0.4

mkdir -p seg out

src_of() { ls raw/"$1"/*.webm | head -1; }

make_title() {
  local out="$1" dur="$2" png="$3"
  local fout
  fout=$(python3 -c "print(${dur} - ${FADE})")
  ffmpeg -y -loop 1 -t "${dur}" -i "png/${png}.png" \
    -vf "fade=t=in:st=0:d=${FADE},fade=t=out:st=${fout}:d=${FADE}" \
    -r "${FPS}" -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p -movflags +faststart "seg/${out}" -loglevel error
  echo "  title: ${out} (${dur}s)"
}

# Full-length clip (no trim) with an optional caption overlay for the tail.
full_clip() {
  local segdir="$1" out="$2" cap="${3:-}"
  local src dur
  src=$(src_of "${segdir}")
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${src}")
  local fout
  fout=$(python3 -c "print(max(${dur} - ${FADE}, 0.1))")
  local scaled="seg/_scaled_${out}"
  ffmpeg -y -i "${src}" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease:flags=lanczos,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,fps=${FPS},format=yuv420p,fade=t=in:st=0:d=${FADE},fade=t=out:st=${fout}:d=${FADE}" \
    -an -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p -movflags +faststart "${scaled}" -loglevel error
  if [[ -n "${cap}" ]]; then
    ffmpeg -y -i "${scaled}" -loop 1 -i "png/${cap}.png" \
      -filter_complex "[0:v][1:v] overlay=(W-w)/2:H-h-60:shortest=1" \
      -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p -movflags +faststart "seg/${out}" -loglevel error
    rm -f "${scaled}"
  else
    mv "${scaled}" "seg/${out}"
  fi
  echo "  clip: ${out} src=${src} (${dur}s)"
}

# Sped-up clip for long real-time waits (e.g. the smoke-test run) — keeps the
# authentic live-streaming footage but compresses idle time like VHS does.
sped_clip() {
  local segdir="$1" out="$2" speed="$3" cap="${4:-}"
  local src
  src=$(src_of "${segdir}")
  local scaled="seg/_scaled_${out}"
  ffmpeg -y -i "${src}" \
    -vf "setpts=PTS/${speed},scale=${W}:${H}:force_original_aspect_ratio=decrease:flags=lanczos,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,fps=${FPS},format=yuv420p,fade=t=in:st=0:d=${FADE}" \
    -an -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p -movflags +faststart "${scaled}" -loglevel error
  if [[ -n "${cap}" ]]; then
    ffmpeg -y -i "${scaled}" -loop 1 -i "png/${cap}.png" \
      -filter_complex "[0:v][1:v] overlay=(W-w)/2:H-h-60:shortest=1" \
      -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p -movflags +faststart "seg/${out}" -loglevel error
    rm -f "${scaled}"
  else
    mv "${scaled}" "seg/${out}"
  fi
  echo "  sped clip (${speed}x): ${out} src=${src}"
}

echo "== Titles =="
make_title "k00-title.mp4"   4.5 "t00-title"
make_title "k01-intro.mp4"   5.5 "t01-intro"
make_title "k02-login.mp4"   2.6 "t02-login"
make_title "k04-dash.mp4"    2.6 "t03-dashboard"
make_title "k06-actions.mp4" 2.6 "t04-actions"
make_title "k08-smoke.mp4"   2.6 "t05-smoke"
make_title "k10-flow.mp4"    2.6 "t06-flow"
make_title "k12-audit.mp4"   2.6 "t07-audit"
make_title "k14-probes.mp4"  2.6 "t08-probes"
make_title "k16-ask.mp4"     2.6 "t09-ask"
make_title "k18-noc.mp4"     2.6 "t10-noc"
make_title "k20-outro.mp4"   4.5 "t11-outro"

echo "== Clips =="
full_clip "seg01-login"     "k03-login.mp4"    "cap-login"
full_clip "seg02-dashboard" "k05-dash.mp4"     "cap-status"
full_clip "seg03-actions"   "k07-actions.mp4"  "cap-actions"
sped_clip "seg04-smoke" "k09-smoke.mp4" 1.8 "cap-smoke"
full_clip "seg05-flow"      "k11-flow.mp4"     "cap-flow"
full_clip "seg06-audit"     "k13-audit.mp4"    "cap-audit"
full_clip "seg07-probes"    "k15-probes.mp4"   "cap-probes"
full_clip "seg08-ask"       "k17-ask.mp4"      "cap-ask"
full_clip "seg09-noc"       "k19-noc.mp4"      "cap-noc"

: > seg/kt-list.txt
for f in k00-title k01-intro \
         k02-login k03-login \
         k04-dash k05-dash \
         k06-actions k07-actions \
         k08-smoke k09-smoke \
         k10-flow k11-flow \
         k12-audit k13-audit \
         k14-probes k15-probes \
         k16-ask k17-ask \
         k18-noc k19-noc \
         k20-outro; do
  echo "file '${f}.mp4'" >> seg/kt-list.txt
done
ffmpeg -y -f concat -safe 0 -i seg/kt-list.txt -c copy out/zyaiqaagent-kt-tutorial.mp4 -loglevel error
echo "== built out/zyaiqaagent-kt-tutorial.mp4 =="
ffprobe -v error -show_entries format=duration -of csv=p=0 out/zyaiqaagent-kt-tutorial.mp4
