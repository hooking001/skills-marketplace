// template/numbering.typ
// ARM Reference Manual numbering system for parts, chapters, sections, appendices, figures, tables, and pages

// State for document phase and appendix tracking
#let doc-phase = state("doc-phase", "front") // "front", "body", "appendix", "back"
#let is-appendix = state("is-appendix", false)

// Helper to convert any content to a clean string
#let to-string(val) = {
  if type(val) == str {
    val
  } else if type(val) == content {
    if val.has("text") {
      val.text
    } else if val.has("children") {
      val.children.map(to-string).join("")
    } else if val.has("body") {
      to-string(val.body)
    } else {
      ""
    }
  } else {
    str(val)
  }
}

// Heading numbering logic
#let arm-heading-numbering(..nums) = {
  let pos = nums.pos()
  if pos.len() == 1 {
    // Level 1: Part A, Part B, Part C...
    let letter = numbering("A", pos.at(0))
    "Part " + letter
  } else if pos.len() == 2 {
    // Level 2: Chapter A1, Chapter A2, Chapter B1... or Appendix C1
    let letter = numbering("A", pos.at(0))
    let ch = str(pos.at(1))
    letter + ch
  } else if pos.len() == 3 {
    // Level 3: Section A1.1, Section B2.3...
    let letter = numbering("A", pos.at(0))
    let ch = str(pos.at(1))
    let sec = str(pos.at(2))
    letter + ch + "." + sec
  } else if pos.len() == 4 {
    // Level 4: Subsection A1.1.1...
    let letter = numbering("A", pos.at(0))
    let ch = str(pos.at(1))
    let sec = str(pos.at(2))
    let sub = str(pos.at(3))
    letter + ch + "." + sec + "." + sub
  } else if pos.len() >= 5 {
    // Level 5: Sub-subsection A1.1.1.1
    let letter = numbering("A", pos.at(0))
    let ch = str(pos.at(1))
    let sec = str(pos.at(2))
    let sub = str(pos.at(3))
    let ssub = str(pos.at(4))
    letter + ch + "." + sec + "." + sub + "." + ssub
  }
}

// Extract chapter identifier from a heading element
#let get-chapter-id(ch-heading) = {
  if ch-heading.numbering != none {
    // Compute numbering for this chapter
    let count = counter(heading).at(ch-heading.location())
    arm-heading-numbering(..count)
  } else {
    // Unnumbered heading like "Glossary"
    to-string(ch-heading.body)
  }
}

// Find the starting physical page of the body
#let get-body-start-page() = {
  let first-body-part = query(heading.where(level: 1)).filter(h => not to-string(h.body).contains("Glossary"))
  let first-body-ch = query(heading.where(level: 2)).filter(h => h.numbering != none)
  let p = 999999
  if first-body-part.len() > 0 {
    p = calc.min(p, first-body-part.first().location().page())
  }
  if first-body-ch.len() > 0 {
    p = calc.min(p, first-body-ch.first().location().page())
  }
  p
}

// Find the active chapter identifier at a given physical page p
#let get-chapter-at-page(p) = {
  // Check if Glossary has started on or before page p
  let gloss-list = query(heading.where(level: 1)).filter(h => to-string(h.body).contains("Glossary"))
  if gloss-list.len() > 0 {
    let g-page = gloss-list.first().location().page()
    if p >= g-page {
      return "Glossary"
    }
  }

  // Front matter pages have no active chapter
  let body-start-p = get-body-start-page()
  if p < body-start-p {
    return ""
  }

  // Find the latest Part heading on or before page p
  let part-list = query(heading.where(level: 1)).filter(h => not to-string(h.body).contains("Glossary") and h.location().page() <= p)
  let last-part-page = if part-list.len() > 0 { part-list.last().location().page() } else { 0 }

  // Check numbered chapter headings on or before page p
  let ch-list = query(heading.where(level: 2)).filter(h => h.numbering != none and h.location().page() <= p)
  if ch-list.len() == 0 {
    return ""
  }

  let last-ch = ch-list.last()
  let last-ch-page = last-ch.location().page()

  // If a new Part started after the last chapter, the previous chapter is no longer active
  if last-part-page > last-ch-page {
    return ""
  }

  get-chapter-id(last-ch)
}

// Common, unified figure/table number string generator (R3-01 fix)
// Evaluates target figure location, ensures Chapter ID and figure counter are strictly
// determined at the TARGET's location, rather than the reference invocation or list site.
#let get-figure-number-string(fig-el) = {
  let target-loc = fig-el.location()
  let target-page = target-loc.page()
  let kind = fig-el.at("kind", default: image)
  let count = counter(figure.where(kind: kind)).at(target-loc)
  let num-val = if count.len() > 0 { count.at(0) } else { 1 }
  let ch = get-chapter-at-page(target-page)
  if ch != "" and ch != "Glossary" {
    ch + "-" + str(num-val)
  } else {
    str(num-val)
  }
}

// Global page number string generator (R4-01 fix)
// Returns lowercase roman for front matter (ii, iii, iv...), and "<ChapterId>-<Page>" for body/back matter.
// Cumulative physical page number is strictly preserved.
#let arm-page-number-string(p) = {
  let gloss-list = query(heading.where(level: 1)).filter(h => to-string(h.body).contains("Glossary"))
  if gloss-list.len() > 0 and p >= gloss-list.first().location().page() {
    return "Glossary-" + str(p)
  }

  let body-start-p = get-body-start-page()
  if p < body-start-p {
    // Front matter uses lowercase roman numerals (ii, iii, iv...)
    if p == 1 {
      "" // Cover has no visible page number
    } else {
      numbering("i", p)
    }
  } else {
    // Body and back matter: Chapter ID + cumulative physical page
    let ch = get-chapter-at-page(p)
    if ch != "" {
      ch + "-" + str(p)
    } else {
      str(p)
    }
  }
}
