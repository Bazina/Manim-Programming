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

/**
 * Convert a camelCase React SVG attribute name to its kebab-case SVG equivalent.
 */
function toSvgAttrName(name) {
  const map = {
    fillRule: "fill-rule",
    clipRule: "clip-rule",
    strokeWidth: "stroke-width",
    strokeLinecap: "stroke-linecap",
    strokeLinejoin: "stroke-linejoin",
    strokeMiterlimit: "stroke-miterlimit",
    fillOpacity: "fill-opacity",
    strokeOpacity: "stroke-opacity",
    strokeDasharray: "stroke-dasharray",
    strokeDashoffset: "stroke-dashoffset",
  };
  return map[name] || name;
}

/**
 * Parse key: "value" pairs from a raw attribute string, stopping before
 * any `children:` key so we don't bleed into nested elements.
 */
function parseAttrs(raw) {
  // Trim up to (but not including) `children:`
  const childIdx = raw.indexOf("children:");
  const attrPart = childIdx >= 0 ? raw.slice(0, childIdx) : raw;

  const attrRe = /(\w+):\s*"([^"]*)"/g;
  let attrs = {};
  let a;
  while ((a = attrRe.exec(attrPart)) !== null) {
    const svgName = toSvgAttrName(a[1]);
    let val = a[2];
    if (val === "currentColor") val = "#FFFFFF";
    attrs[svgName] = val;
  }
  return attrs;
}

function attrsToString(attrs) {
  return Object.entries(attrs)
    .map(([k, v]) => `${k}="${v}"`)
    .join(" ");
}

/**
 * Recursively extract SVG element calls from a block of JSX-like code.
 * Handles both leaf elements:  jsx("path", { d: "…", fill: "…" })
 * and group elements:          jsxs("g", { opacity: "0.5", children: [ … ] })
 *
 * Returns an array of SVG markup strings.
 */
function extractElements(block, jsx, jsxs, indent) {
  const ind = " ".repeat(indent);
  const results = [];

  // Match both jsx and jsxs calls that create a named SVG element (not Fragment)
  // We need to find each call, then figure out its full extent including children.
  const funcPat = `(?:${escapeRegExp(jsx)}|${escapeRegExp(jsxs)})`;
  // Match the opening:  func("tagName", {
  const openRe = new RegExp(funcPat + `\\("(\\w+)",\\s*\\{`, "g");

  let om;
  while ((om = openRe.exec(block)) !== null) {
    const tag = om[1];
    const attrStart = om.index + om[0].length; // right after the opening {

    // Find the matching closing } by counting braces
    let depth = 1;
    let pos = attrStart;
    while (pos < block.length && depth > 0) {
      if (block[pos] === "{") depth++;
      else if (block[pos] === "}") depth--;
      pos++;
    }
    // pos now points right after the matching }
    const innerBlock = block.slice(attrStart, pos - 1);

    const attrs = parseAttrs(innerBlock);
    const attrStr = attrsToString(attrs);

    // Check if this element has children
    const childMatch = innerBlock.match(/children:\s*\[/);
    if (childMatch) {
      // It's a group element (like <g>) — recurse into its children block
      const childStart = innerBlock.indexOf("children:") + "children:".length;
      const childBlock = innerBlock.slice(childStart);

      const childElems = extractElements(childBlock, jsx, jsxs, indent + 2);

      if (childElems.length > 0) {
        results.push(`${ind}<${tag}${attrStr ? " " + attrStr : ""}>`);
        results.push(...childElems);
        results.push(`${ind}</${tag}>`);
      }
    } else {
      // Leaf element (path, circle, rect, etc.)
      if (attrStr) {
        results.push(`${ind}<${tag} ${attrStr}/>`);
      }
    }

    // Advance openRe past this entire element to avoid re-matching children
    openRe.lastIndex = pos;
  }

  return results;
}

/** Turn JSX-like tokens inside a .mjs file into SVG markup for a given variant */
function extractVariantSVG(mjsContent, variant) {
  const { jsx, jsxs } = parseImportNames(mjsContent);

  // Find the block for this variant in the Map
  const variantEsc = variant.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // Locate  ["VariantName",  in the source
  const startRe = new RegExp(`\\["${variantEsc}"\\s*,`);
  const startMatch = startRe.exec(mjsContent);
  if (!startMatch) return null;

  // From the variant start, find the balanced block by tracking brackets
  // until we reach the closing  ]  of this variant entry.
  let depth = 0;
  let pos = startMatch.index;
  let started = false;
  while (pos < mjsContent.length) {
    const ch = mjsContent[pos];
    if (ch === "[") { depth++; started = true; }
    else if (ch === "]") { depth--; }
    if (started && depth === 0) break;
    pos++;
  }
  const block = mjsContent.slice(startMatch.index, pos + 1);

  const elems = extractElements(block, jsx, jsxs, 2);
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

