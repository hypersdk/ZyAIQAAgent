#!/usr/bin/env node
/** Convert a local HTML file to PDF using Playwright (Chromium print). */
import { chromium } from "@playwright/test";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [, , htmlArg, pdfArg] = process.argv;

if (!htmlArg || !pdfArg) {
  console.error("Usage: node html-to-pdf.mjs <input.html> <output.pdf>");
  process.exit(1);
}

const htmlPath = path.resolve(htmlArg);
const pdfPath = path.resolve(pdfArg);

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle" });
  await page.pdf({
    path: pdfPath,
    format: "A4",
    printBackground: true,
    margin: { top: "20mm", bottom: "20mm", left: "15mm", right: "15mm" },
  });
  console.log(`PDF written to ${pdfPath}`);
} finally {
  await browser.close();
}
