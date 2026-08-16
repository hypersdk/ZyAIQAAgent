// Copyright 2026 ZyvorAI Labs Private Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! Screenshot diff utility for Zyvor Argus.
//! Called from Python when ENABLE_RUST_PROCESSOR=true.

use clap::Parser;
use image::{ImageBuffer, Rgb};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "zyvor-diff")]
struct Args {
    #[arg(long)]
    baseline: PathBuf,
    #[arg(long)]
    current: PathBuf,
    #[arg(long)]
    diff_output: PathBuf,
    #[arg(long, default_value_t = 1.0)]
    threshold: f64,
}

fn diff_percent(img1: &ImageBuffer<Rgb<u8>, Vec<u8>>, img2: &ImageBuffer<Rgb<u8>, Vec<u8>>) -> f64 {
    let mut changed = 0u64;
    let total = (img1.width() * img1.height() * 3) as u64;
    for (p1, p2) in img1.pixels().zip(img2.pixels()) {
        if p1 != p2 {
            changed += 3;
        }
    }
    if total == 0 {
        return 0.0;
    }
    (changed as f64 / total as f64) * 100.0
}

fn main() {
    let args = Args::parse();

    let base = image::open(&args.baseline).expect("open baseline").into_rgb8();
    let mut curr = image::open(&args.current).expect("open current").into_rgb8();

    if base.dimensions() != curr.dimensions() {
        curr = image::imageops::resize(
            &curr,
            base.width(),
            base.height(),
            image::imageops::FilterType::Triangle,
        );
    }

    let mut diff_img = ImageBuffer::new(base.width(), base.height());
    for (x, y, p1) in base.enumerate_pixels() {
        let p2 = curr.get_pixel(x, y);
        let diff_pixel = if p1 == p2 {
            Rgb([0, 0, 0])
        } else {
            Rgb([
                p1[0].abs_diff(p2[0]),
                p1[1].abs_diff(p2[1]),
                p1[2].abs_diff(p2[2]),
            ])
        };
        diff_img.put_pixel(x, y, diff_pixel);
    }

    diff_img.save(&args.diff_output).expect("save diff");
    let pct = diff_percent(&base, &curr);
    let passed = pct <= args.threshold;

    let result = serde_json::json!({
        "baseline": args.baseline,
        "current": args.current,
        "diff_output": args.diff_output,
        "diff_percent": pct,
        "threshold": args.threshold,
        "passed": passed,
    });

    println!("{}", serde_json::to_string(&result).unwrap());
    if !passed {
        std::process::exit(1);
    }
}
