#!/usr/bin/env node
/**
 * convert-to-webp.js
 * Converts all PNG/JPG images under assets/images to WebP at 85% quality.
 * Skips favicon files (must remain PNG for browser compatibility).
 * Reports original vs. new size and % savings per file.
 */

const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

const IMAGE_DIR = path.join(__dirname, "assets", "images");
const QUALITY = 85;

// Favicons must stay PNG — skip them
const SKIP_DIRS = ["favicons"];

function walk(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir)) {
    const full = path.join(dir, entry);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      if (!SKIP_DIRS.includes(entry)) results.push(...walk(full));
    } else if (/\.(png|jpe?g)$/i.test(entry)) {
      results.push(full);
    }
  }
  return results;
}

function fmt(bytes) {
  return (bytes / 1024).toFixed(1) + " KB";
}

async function convert(srcPath) {
  const webpPath = srcPath.replace(/\.(png|jpe?g)$/i, ".webp");

  // Skip if WebP already newer than source
  if (fs.existsSync(webpPath)) {
    const srcMtime = fs.statSync(srcPath).mtimeMs;
    const webpMtime = fs.statSync(webpPath).mtimeMs;
    if (webpMtime > srcMtime) return null; // already up to date
  }

  await sharp(srcPath).webp({ quality: QUALITY }).toFile(webpPath);

  const origSize = fs.statSync(srcPath).size;
  const newSize = fs.statSync(webpPath).size;
  const saved = origSize - newSize;
  const pct = ((saved / origSize) * 100).toFixed(1);

  return { srcPath, webpPath, origSize, newSize, saved, pct };
}

async function main() {
  const files = walk(IMAGE_DIR);
  console.log(`\nFound ${files.length} PNG/JPG files (excluding favicons)\n`);
  console.log(
    "File".padEnd(62) +
      "Original".padStart(10) +
      "WebP".padStart(10) +
      "Saved".padStart(10) +
      "Reduction".padStart(11)
  );
  console.log("─".repeat(103));

  let totalOrig = 0;
  let totalNew = 0;
  let converted = 0;
  let skipped = 0;

  for (const f of files) {
    const result = await convert(f);
    if (!result) {
      skipped++;
      continue;
    }
    const rel = path.relative(__dirname, result.srcPath);
    totalOrig += result.origSize;
    totalNew += result.newSize;
    converted++;

    const sign = result.saved >= 0 ? "-" : "+";
    const savedStr =
      result.saved >= 0
        ? sign + fmt(Math.abs(result.saved))
        : sign + fmt(Math.abs(result.saved));
    console.log(
      rel.padEnd(62) +
        fmt(result.origSize).padStart(10) +
        fmt(result.newSize).padStart(10) +
        savedStr.padStart(10) +
        (result.pct + "%").padStart(11)
    );
  }

  const totalSaved = totalOrig - totalNew;
  const totalPct = ((totalSaved / totalOrig) * 100).toFixed(1);

  console.log("─".repeat(103));
  console.log(
    `${"TOTAL (" + converted + " files converted, " + skipped + " skipped)"}`.padEnd(62) +
      fmt(totalOrig).padStart(10) +
      fmt(totalNew).padStart(10) +
      ("-" + fmt(totalSaved)).padStart(10) +
      (totalPct + "%").padStart(11)
  );

  console.log(`\n✓ Total saved: ${fmt(totalSaved)} (${totalPct}% reduction)`);
  console.log(
    `  Original total: ${fmt(totalOrig)} → WebP total: ${fmt(totalNew)}\n`
  );
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
