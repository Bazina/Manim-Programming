/**
 * Extract Solar Icons from @solar-icons/react .mjs definition files
 * and write them as standalone SVG files into assets/icons/
 *
 * Usage:  node extract_solar_icons.js [category/IconName] [variant]
 * Examples:
 *   node extract_solar_icons.js users/UserCircle Bold
 *   node extract_solar_icons.js users/User Linear
 *   node extract_solar_icons.js                          (extracts ALL icons, all variants)
 */

const fs = require("fs");
const path = require("path");

const DEFS_ROOT = path.join(
  __dirname,
  "node_modules",
  "@solar-icons",
  "react",
  "dist",
  "esm",
  "defs"
);
const OUT_DIR = path.join(__dirname, "assets", "icons");

// ── helpers ──────────────────────────────────────────────────────────

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Parse the import line to discover which local variable names correspond
 * to `jsx` and `jsxs`.  The bundler may minify them to any single letter.
 *
 * Example import lines:
 *   import { jsxs as t, jsx as r, Fragment as C } from "react/jsx-runtime";
 *   import { jsxs as o, jsx as C, Fragment as r } from "react/jsx-runtime";
 */
function parseImportNames(mjsContent) {
  const m = mjsContent.match(
    /import\s*\{([^}]+)\}\s*from\s*["']react\/jsx-runtime["']/
  );
  if (!m) return { jsx: "r", jsxs: "t" }; // fallback
  const mapping = {};
  const parts = m[1].split(",");
  for (const part of parts) {
    const pair = part.trim().match(/^(\w+)\s+as\s+(\w+)$/);
    if (pair) mapping[pair[1]] = pair[2];
  }
  return {
    jsx: mapping["jsx"] || "r",
    jsxs: mapping["jsxs"] || "t",
  };
}

/** Turn JSX-like tokens inside a .mjs file into SVG markup for a given variant */
function extractVariantSVG(mjsContent, variant) {
  const { jsx, jsxs } = parseImportNames(mjsContent);

  // The file stores a Map of [variantName, jsx].
  // We'll use regex to grab the raw attributes from path / circle / rect elements
  // for the requested variant.

  // Find the block for the variant.  Structure:
  //   ["Bold", /* ... */ r("path", { ... }) ]
  const variantEsc = variant.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // Grab everything between  ["<variant>",  and the next  "],  or  "])
  const blockRe = new RegExp(
    `\\["${variantEsc}"[\\s\\S]*?children:[\\s\\S]*?\\}\\)\\s*\\]`,
    "g"
  );
  const match = mjsContent.match(blockRe);
  if (!match) return null;

  const block = match[0];

  // Extract every element call:  <jsx>|<jsxs>("tag", { key: "val", ... })
  // Both jsx and jsxs can create SVG elements – we need to match either.
  const funcPattern = `(?:${escapeRegExp(jsx)}|${escapeRegExp(jsxs)})`;
  const elemRe = new RegExp(funcPattern + `\\("(\\w+)",\\s*\\{([^}]+)\\}\\)`, "g");
  let elems = [];
  let em;
  while ((em = elemRe.exec(block)) !== null) {
    const tag = em[1];
    const attrsRaw = em[2];
    // Parse key: "value" pairs
    const attrRe = /(\w+):\s*"([^"]*)"/g;
    let attrs = {};
    let a;
    while ((a = attrRe.exec(attrsRaw)) !== null) {
      // Convert camelCase React attr names to SVG kebab-case
      const svgAttr = a[1]
        .replace("fillRule", "fill-rule")
        .replace("clipRule", "clip-rule")
        .replace("strokeWidth", "stroke-width")
        .replace("strokeLinecap", "stroke-linecap")
        .replace("strokeLinejoin", "stroke-linejoin")
        .replace("strokeMiterlimit", "stroke-miterlimit")
        .replace("fillOpacity", "fill-opacity")
        .replace("strokeOpacity", "stroke-opacity");
      attrs[svgAttr] = a[2];
    }
    // Replace currentColor with white so it's visible on dark backgrounds
    // (you can re-color in Manim later)
    for (const k of Object.keys(attrs)) {
      if (attrs[k] === "currentColor") attrs[k] = "#FFFFFF";
    }
    const attrStr = Object.entries(attrs)
      .map(([k, v]) => `${k}="${v}"`)
      .join(" ");
    elems.push(`  <${tag} ${attrStr}/>`);
  }

  if (elems.length === 0) return null;

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">`,
    ...elems,
    `</svg>`,
  ].join("\n");
}

// ── main ─────────────────────────────────────────────────────────────

function extractIcon(category, iconName, variant) {
  const mjsPath = path.join(DEFS_ROOT, category, `${iconName}.mjs`);
  if (!fs.existsSync(mjsPath)) {
    console.error(`File not found: ${mjsPath}`);
    return;
  }
  const content = fs.readFileSync(mjsPath, "utf-8");
  const svg = extractVariantSVG(content, variant);
  if (!svg) {
    console.error(`Variant "${variant}" not found in ${category}/${iconName}`);
    return;
  }

  const outSubDir = path.join(OUT_DIR, category);
  fs.mkdirSync(outSubDir, { recursive: true });
  const outFile = path.join(outSubDir, `${iconName}${variant}.svg`);
  fs.writeFileSync(outFile, svg, "utf-8");
  console.log(`✓ ${outFile}`);
}

function extractAll() {
  const variants = [
    "Bold",
    "BoldDuotone",
    "Broken",
    "LineDuotone",
    "Linear",
    "Outline",
  ];
  const categories = fs.readdirSync(DEFS_ROOT).filter((f) =>
    fs.statSync(path.join(DEFS_ROOT, f)).isDirectory()
  );
  let count = 0;
  for (const cat of categories) {
    const files = fs.readdirSync(path.join(DEFS_ROOT, cat));
    for (const file of files) {
      if (!file.endsWith(".mjs")) continue;
      const iconName = file.replace(".mjs", "");
      const content = fs.readFileSync(
        path.join(DEFS_ROOT, cat, file),
        "utf-8"
      );
      for (const v of variants) {
        const svg = extractVariantSVG(content, v);
        if (svg) {
          const outSubDir = path.join(OUT_DIR, cat);
          fs.mkdirSync(outSubDir, { recursive: true });
          const outFile = path.join(outSubDir, `${iconName}${v}.svg`);
          fs.writeFileSync(outFile, svg, "utf-8");
          count++;
        }
      }
    }
  }
  console.log(`\n✓ Extracted ${count} SVG icons into ${OUT_DIR}`);
}

// ── CLI ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

if (args.length === 0) {
  // Extract all
  extractAll();
} else {
  const [catIcon, variant = "Bold"] = args;
  const parts = catIcon.split("/");
  if (parts.length !== 2) {
    console.error("Usage: node extract_solar_icons.js category/IconName [variant]");
    console.error("  e.g. node extract_solar_icons.js users/UserCircle Bold");
    process.exit(1);
  }
  extractIcon(parts[0], parts[1], variant);
}

