// template/crossref.typ
// ARM Reference Manual hyperlinking and smart cross-referencing system

#import "typography.typ": *
#import "numbering.typ": arm-heading-numbering, arm-page-number-string, is-appendix, get-figure-number-string

// Document state for cross-reference styling
#let doc-link-color = state("doc-link-color", arm-blue)
#let doc-ref-italic = state("doc-ref-italic", false)

// Helper to extract figure/table number and caption text
// Uses get-figure-number-string(fig-el) to ensure numbering is strictly tied to the TARGET's location (R3-01).
#let extract-figure-info(fig-el) = {
  let kind = fig-el.at("kind", default: image)
  let prefix = if kind == table or kind == "table" { "Table" } else { "Figure" }
  let fig-num = get-figure-number-string(fig-el)
  let num-str = prefix + " " + fig-num

  let cap-str = if fig-el.has("caption") and fig-el.caption != none {
    fig-el.caption.body
  } else {
    ""
  }

  (num: num-str, title: cap-str)
}

// Master Cross-Reference Function
#let arm-ref(
  target,
  form: "full",              // "num", "title", "num-title", "page", "full"
  italic: auto,              // auto uses doc-ref-italic state, or true/false
  text-override: none,       // Custom link text if desired
) = context {
  let active-link-color = doc-link-color.get()
  let use-italic = if italic == auto { doc-ref-italic.get() } else { italic }

  let matches = query(target)
  assert(
    matches.len() > 0,
    message: "arm-ref: unresolved cross-reference label " + repr(target) + ". Ensure the target label is defined."
  )

  let el = matches.first()
  let target-loc = el.location()
  let target-page = target-loc.page()
  let here-page = here().page()

  // Compute target page formatted string
  let target-page-str = arm-page-number-string(target-page)

  // Extract number and title strictly based on semantic element type
  let num-text = ""
  let title-text = ""

  if el.func() == heading {
    let count = counter(heading).at(target-loc)
    if el.level == 1 {
      // Part heading
      if el.numbering != none {
        num-text = arm-heading-numbering(..count)
      }
      title-text = el.body
    } else if el.level == 2 {
      // Chapter or Appendix heading
      let in-app = is-appendix.at(target-loc)
      let prefix = if in-app { "Appendix " } else { "Chapter " }
      if el.numbering != none {
        num-text = prefix + arm-heading-numbering(..count)
      }
      title-text = el.body
    } else {
      // Section or Subsection
      if el.numbering != none {
        num-text = arm-heading-numbering(..count)
      }
      title-text = el.body
    }
  } else if el.func() == figure {
    let info = extract-figure-info(el)
    num-text = info.num
    title-text = info.title
  } else if el.func() == metadata and type(el.value) == dictionary and el.value.at("kind", default: "") == "glossary" {
    // Glossary entry anchor
    num-text = ""
    title-text = el.value.term
  } else {
    // Unsupported element: raise explicit error rather than dumping content body
    panic(
      "arm-ref: unsupported target element type " + repr(el.func()) +
      " for label " + repr(target) +
      ". Labels must be attached to heading, figure/table, or glossary-entry."
    )
  }

  // Construct label output based on requested form
  let ref-content = if text-override != none {
    text-override
  } else if form == "num" {
    num-text
  } else if form == "title" {
    title-text
  } else if form == "num-title" {
    if num-text != "" and title-text != "" {
      [#num-text #title-text]
    } else if num-text != "" {
      num-text
    } else {
      title-text
    }
  } else if form == "page" {
    target-page-str
  } else {
    // "full" (default): num-title [+ "on page ..." if on different page]
    let base-str = if num-text != "" and title-text != "" {
      [#num-text #title-text]
    } else if num-text != "" {
      num-text
    } else {
      title-text
    }

    if target-page == here-page {
      // Same-page reference: omit page string per ARM standard
      base-str
    } else {
      // Cross-page reference: append "on page <target-page-str>"
      [#base-str on page #target-page-str]
    }
  }

  // Apply italic styling if requested
  let styled-content = if use-italic {
    emph(ref-content)
  } else {
    ref-content
  }

  // Wrap in clickable link
  link(target-loc)[#text(fill: active-link-color)[#styled-content]]
}

// Convenience wrapper for referencing glossary terms
#let ref-glossary(target, italic: false) = {
  arm-ref(target, form: "title", italic: italic)
}
