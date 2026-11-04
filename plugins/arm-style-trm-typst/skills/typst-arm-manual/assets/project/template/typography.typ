// template/typography.typ
// Typography settings, fonts, colors, and sizing for ARM Reference Manual style with Pretendard

// Primary font families using Pretendard as the default typeface for all text roles,
// with clean cross-platform fallbacks without missing-font warnings.
#let font-main = (
  "Pretendard",
  "Arial",
)

// In accordance with the user instruction, Pretendard serves as the primary font
// for body, headings, tables, navigation, and running headers/footers.
#let font-serif = font-main
#let font-sans = font-main

// Code and monospace font chain with Pretendard fallback for Korean comments
#let font-mono = (
  "Menlo",
  "Courier New",
  "Pretendard",
)

// Document color palette
#let arm-blue = rgb("#1212cc")          // Standard ARM hyper-reference blue
#let arm-black = rgb("#000000")
#let arm-dark-gray = rgb("#2b2b2b")
#let arm-muted-gray = rgb("#555555")
#let arm-border-gray = rgb("#aaaaaa")
#let arm-rule-gray = rgb("#cccccc")       // Thin footer rule line (0.5pt)
#let arm-light-gray = rgb("#f5f6f8")
#let arm-res-gray = rgb("#e9ecef")       // Reserved register bits fill

// Font size hierarchy (in points)
#let size-doc-title = 24pt
#let size-part-num = 24pt
#let size-part-title = 20pt
#let size-chap-num = 20pt
#let size-chap-title = 20pt
#let size-sec = 12pt
#let size-subsec = 10.5pt
#let size-subsubsec = 9.5pt
#let size-body = 10pt                     // Updated to 10pt for improved legibility per user request
#let size-header = 8pt
#let size-footer = 8pt
#let size-caption = 9pt
#let size-table = 8.5pt
#let size-code = 8.5pt
#let size-bit-idx = 7pt
#let size-bit-name = 7.5pt

// Line leading (proportional spacing)
// In Typst, size 10pt with leading 0.75em produces an actual baseline-to-baseline distance of ~14.6pt,
// satisfying the target consecutive line distance of 14-16pt.
#let leading-body = 0.75em
#let leading-tight = 0.45em
#let leading-code = 0.55em

// Paragraph and vertical block spacing
#let spacing-par = 1.2em
#let spacing-list = 0.75em
#let table-inset-default = (x: 6pt, y: 5pt)

// Helper: Check if string consists purely of ASCII characters (no Hangul or CJK)
#let is-pure-ascii(s) = {
  if type(s) != str { return false }
  let cps = s.clusters()
  for c in cps {
    let code = str.to-unicode(c)
    if code > 127 { return false }
  }
  true
}

// ASCII-safe small caps helper:
// Note: Pretendard-Regular.otf does NOT contain the OpenType 'smcp' feature in its GSUB table
// (Pretendard v1.3.9 static OTF). Typst therefore synthesizes small caps.
// This helper applies smallcaps exclusively to ASCII text and preserves Hangul glyphs intact.
#let smallcaps-term(it) = {
  if type(it) == str {
    if is-pure-ascii(it) {
      smallcaps(it)
    } else {
      it
    }
  } else if type(it) == content {
    if it.has("text") {
      let t = it.text
      if is-pure-ascii(t) {
        smallcaps(it)
      } else {
        it
      }
    } else if it.has("children") {
      it.children.map(smallcaps-term).join("")
    } else {
      it
    }
  } else {
    it
  }
}
