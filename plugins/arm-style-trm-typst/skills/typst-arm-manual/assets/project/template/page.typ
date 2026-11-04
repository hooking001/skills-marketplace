// template/page.typ
// Page geometry, header/footer configuration, duplex margins, and recto control

#import "typography.typ": *
#import "numbering.typ": *

// Page dimensions
#let size-arm-letter = (width: 595pt, height: 792pt)
#let size-a4 = (width: 595.28pt, height: 841.89pt)

// Standard ARM layout margins (in points)
#let margin-top = 46pt
#let margin-bottom = 60pt
#let margin-left-body = 132.5pt      // Indented body column left edge
#let margin-left-gutter = 51.7pt    // Gutter edge for hanging numbers & wide blocks
#let margin-right = 53pt            // Right text edge
#let gutter-width = 80.8pt          // margin-left-body - margin-left-gutter (80.8pt)
#let printable-width = 490.3pt      // 595 - 51.7 - 53 (490.3pt)

// Calculate dynamic dimensions based on paper selection
#let get-page-dimensions(paper) = {
  if paper == "a4" {
    let w = size-a4.width
    let h = size-a4.height
    (
      width: w,
      height: h,
      printable-width: w - margin-left-gutter - margin-right,
      body-width: w - margin-left-body - margin-right,
      gutter-width: margin-left-body - margin-left-gutter,
    )
  } else {
    let w = size-arm-letter.width
    let h = size-arm-letter.height
    (
      width: w,
      height: h,
      printable-width: w - margin-left-gutter - margin-right,
      body-width: w - margin-left-body - margin-right,
      gutter-width: margin-left-body - margin-left-gutter,
    )
  }
}

// Check whether page p contains content (suppress header/footer on blank pages)
#let page-has-content(p) = {
  if query(metadata.where(value: "page-content")).any(m => m.location().page() == p) {
    return true
  }
  let starts = query(metadata.where(value: "content-start"))
  let ends = query(metadata.where(value: "content-end"))
  for (s, e) in starts.zip(ends) {
    if s.location().page() <= p and p <= e.location().page() {
      return true
    }
  }
  return false
}

// Header generation
#let arm-header(doc-info) = context {
  let p = here().page()
  if p == 1 {
    // Cover page has no header
    return none
  }

  // Check if this page has content (suppress on blank pages)
  if not page-has-content(p) {
    return none
  }

  // Suppress headers on Part start page (level 1) or Chapter start page (level 2)
  let h-on-page = query(heading).filter(h => h.location().page() == p)
  if h-on-page.any(h => h.level == 1 or h.level == 2) {
    return none
  }

  // Front matter pages before body chapters
  let body-start-p = get-body-start-page()

  if p < body-start-p {
    // In front matter:
    // Check for explicit frontmatter section marker
    let fm-markers = query(metadata).filter(m => {
      type(m.value) == dictionary and m.value.at("kind", default: "") == "frontmatter-section" and m.location().page() <= p
    })

    let active-fm = if fm-markers.len() > 0 { fm-markers.last().value.at("title", default: "") } else { "" }

    // Check unnumbered level 2 headings in front matter (e.g. Preface)
    let pref-h = query(heading.where(level: 2)).filter(h => h.numbering == none and h.location().page() <= p)
    if pref-h.len() > 0 {
      let p-last = pref-h.last()
      let fm-last-p = if fm-markers.len() > 0 { fm-markers.last().location().page() } else { 0 }
      if p-last.location().page() >= fm-last-p {
        active-fm = to-string(p-last.body)
      }
    }

    if active-fm == "" {
      // Release info (p=2) or Doc admin (p=3) in front matter: suppress running header per ARM convention
      return none
    }

    let is-odd = calc.odd(p)
    let align-dir = if is-odd { right } else { left }
    return pad(left: -gutter-width)[
      #align(align-dir)[
        #set text(font: font-sans, size: size-header, fill: arm-muted-gray)
        #active-fm
      ]
    ]
  }

  // Check if we are on the Glossary page
  let gloss-h = query(heading.where(level: 1)).filter(h => to-string(h.body).contains("Glossary"))
  if gloss-h.len() > 0 and p >= gloss-h.first().location().page() {
    let is-odd = calc.odd(p)
    let align-dir = if is-odd { right } else { left }
    return pad(left: -gutter-width)[
      #align(align-dir)[
        #set text(font: font-sans, size: size-header, fill: arm-dark-gray)
        Glossary
      ]
    ]
  }

  // Determine active Chapter in body
  let ch-list = query(heading.where(level: 2)).filter(h => h.numbering != none and h.location().page() <= p)
  if ch-list.len() == 0 {
    return none
  }

  let cur-ch = ch-list.last()
  let ch-page = cur-ch.location().page()

  // Check if a new Part started after the last chapter
  let part-list = query(heading.where(level: 1)).filter(h => not to-string(h.body).contains("Glossary") and h.location().page() <= p)
  if part-list.len() > 0 and part-list.last().location().page() > ch-page {
    return none
  }

  let in-app = is-appendix.at(cur-ch.location())
  let prefix = if in-app { "Appendix " } else { "Chapter " }

  let ch-num = if cur-ch.numbering != none {
    let count = counter(heading).at(cur-ch.location())
    arm-heading-numbering(..count) + " "
  } else {
    ""
  }
  let ch-str = [#ch-num#cur-ch.body]

  // Find active section (R4-03 fix):
  // 1. Prioritize level 3 section starting on the current page (within current chapter)
  //    Policy for section-pagebreak: false (multiple sections on page): take the first section on that page.
  // 2. If no section starts on the current page, find the active section continuing into this page.
  //    Strictly prevent crossing Chapter boundaries.
  let sec-on-page = query(heading.where(level: 3)).filter(h => h.location().page() == p and h.location().page() >= ch-page)
  let cur-sec = none
  if sec-on-page.len() > 0 {
    cur-sec = sec-on-page.first()
  } else {
    let sec-before = query(heading.where(level: 3)).filter(h => h.location().page() < p and h.location().page() >= ch-page)
    if sec-before.len() > 0 {
      cur-sec = sec-before.last()
    }
  }

  let sec-str = if cur-sec != none {
    let s-num = if cur-sec.numbering != none {
      let count = counter(heading).at(cur-sec.location())
      arm-heading-numbering(..count) + " "
    } else {
      ""
    }
    [#s-num#cur-sec.body]
  } else {
    ""
  }

  let is-odd = calc.odd(p)
  let align-dir = if is-odd { right } else { left }

  // Render header in the hanging gutter + body width (flush with outer margins)
  pad(left: -gutter-width)[
    #align(align-dir)[
      #set text(font: font-sans, size: size-header, fill: arm-dark-gray)
      #block(spacing: 2pt)[
        #ch-str
        #if sec-str != "" [ \ #sec-str ]
      ]
    ]
  ]
}

// Footer generation with thin rule matching ARM reference standard
#let arm-footer(doc-info) = context {
  let p = here().page()
  if p == 1 {
    // Cover page footer is handled separately on the cover page itself
    return none
  }

  // Check if this page is blank
  if not page-has-content(p) {
    return none
  }

  // Check if this page is a Part start page (R4-02 fix: suppress footer and rule on Part pages)
  let h-on-page = query(heading).filter(h => h.location().page() == p)
  if h-on-page.any(h => h.level == 1 and not to-string(h.body).contains("Glossary")) {
    return none
  }

  let doc-id = doc-info.at("doc-id", default: "")
  let issue = doc-info.at("issue", default: "")
  let issue-id = doc-info.at("issue-id", default: "")
  let conf = doc-info.at("confidentiality", default: "Non-Confidential")
  let copyright = doc-info.at("copyright-short", default: "Copyright © 2026. All rights reserved.")
  let page-str = arm-page-number-string(p)

  let is-odd = calc.odd(p)

  pad(left: -gutter-width)[
    #block(width: 100%)[
      // Thin rule 0.5pt above footer spanning x=51.7pt to x=542.0pt at y=750.0pt
      #line(length: 100%, stroke: 0.5pt + arm-rule-gray)
      #v(4pt)
      #set text(font: font-sans, size: size-footer, fill: arm-dark-gray)

      #if is-odd [
        // Odd page footer (Recto): Doc ID on left, Copyright center, Page on right
        #grid(
          columns: (1fr, 2fr, 1fr),
          align: (left, center, right),
          [#doc-id #if issue != "" [ #issue ]],
          [#copyright],
          [#strong(page-str)],
        )
        #v(1pt)
        #grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [#text(fill: arm-muted-gray)[#conf]],
          [#if issue-id != "" [#text(fill: arm-muted-gray)[#issue-id]]],
        )
      ] else [
        // Even page footer (Verso): Page on left, Copyright center, Doc ID on right
        #grid(
          columns: (1fr, 2fr, 1fr),
          align: (left, center, right),
          [#strong(page-str)],
          [#copyright],
          [#doc-id #if issue != "" [ #issue ]],
        )
        #v(1pt)
        #grid(
          columns: (1fr, 1fr),
          align: (left, right),
          [#if issue-id != "" [#text(fill: arm-muted-gray)[#issue-id]]],
          [#text(fill: arm-muted-gray)[#conf]],
        )
      ]
    ]
  ]
}
