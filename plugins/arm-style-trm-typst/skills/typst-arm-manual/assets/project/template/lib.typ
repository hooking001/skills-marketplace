// template/lib.typ
// Master entry point for the ARM Architecture Reference Manual Typst Template

#import "typography.typ": *
#import "numbering.typ": *
#import "page.typ": *
#import "frontmatter.typ": *
#import "components.typ": *
#import "crossref.typ": *

// Helper to start the Appendix section
#let start-appendix() = {
  is-appendix.update(true)
  doc-phase.update("appendix")
}

// Master document template function
#let arm-doc(
  doc-info: (:),
  paper: "arm-letter",       // "arm-letter" (595x792pt) or "a4" (595.28x841.89pt)
  recto: true,               // Whether Part and Chapter pages enforce odd/recto start
  section-pagebreak: true,   // User Requirement 1: Chapter and A.B sections each start on a new page
  body-size: size-body,      // 10pt default
  body-leading: leading-body,// 0.75em default (~14.6pt consecutive line baseline distance)
  par-spacing: spacing-par,  // 1.2em paragraph spacing
  link-color: arm-blue,
  ref-italic: false,
  print-mode: false,
  table-inset: table-inset-default, // Central table inset (x: 6pt, y: 5pt)
  body,
) = {
  let doc-title = doc-info.at("title", default: "Technical Reference Manual")
  let doc-authors = doc-info.at("author", default: doc-info.at("team", default: "Architecture Team"))

  // Save doc-info into global state for frontmatter pages and footers
  doc-info-state.update(doc-info)

  // Set PDF document properties
  set document(
    title: doc-title,
    author: doc-authors,
    date: auto,
  )

  // Configure document link styling state
  let effective-link-color = if print-mode { arm-black } else { link-color }
  doc-link-color.update(effective-link-color)
  doc-ref-italic.update(ref-italic)

  // Determine page dimensions
  let page-dim = get-page-dimensions(paper)

  // Base Page Settings
  set page(
    width: page-dim.width,
    height: page-dim.height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left-body,
      right: margin-right,
    ),
    header: arm-header(doc-info),
    footer: arm-footer(doc-info),
    numbering: (..nums) => context {
      arm-page-number-string(nums.pos().at(0))
    },
  )

  // Base Typography using Pretendard
  set text(
    font: font-main,
    size: body-size,
    fill: arm-black,
    lang: "en",
    spacing: 100%,
  )
  set par(
    leading: body-leading,
    spacing: par-spacing,
    justify: true,
  )
  set list(spacing: spacing-list)
  set enum(spacing: spacing-list)

  // Table settings and breaking policy (R3-02, R4-06):
  // Table cell inset is centrally controlled via table-inset parameter (default x: 6pt, y: 5pt).
  // ONLY tables are permitted to split across page boundaries.
  // General figures (diagrams, images, bitfields) are strictly atomic and non-breakable.
  set table(inset: table-inset)
  show figure.where(kind: table): set block(breakable: true)
  show figure.where(kind: image): set block(breakable: false)

  // Chapter-prefixed Figure and Table Numbering (e.g. Figure A1-1, Table B1-2)
  set figure(numbering: (..nums) => context {
    let ch = get-chapter-at-page(here().page())
    if ch != "" and ch != "Glossary" {
      ch + "-" + str(nums.pos().at(0))
    } else {
      str(nums.pos().at(0))
    }
  })

  // Code & Monospace styling with Pretendard fallback for Korean comments
  show raw: it => {
    if it.block {
      block(
        width: 100%,
        fill: arm-light-gray,
        stroke: 0.5pt + arm-border-gray,
        inset: (x: 8pt, y: 7pt),
        radius: 1pt,
        [
          #set text(font: font-mono, size: size-code, fill: arm-black)
          #set par(leading: leading-code, justify: false)
          #it
        ]
      )
    } else {
      text(font: font-mono, size: 0.92em, fill: arm-dark-gray)[#it]
    }
  }

  // Hyperlink styling (external URL links respect print-mode and link-color)
  show link: it => {
    if type(it.dest) == str {
      text(fill: effective-link-color, it)
    } else {
      it
    }
  }

  // Caption styling: Right-aligned, Arial/Pretendard bold/regular 9pt
  show figure.caption: it => {
    align(right)[
      #set text(font: font-sans, size: size-caption, fill: arm-black)
      #block(width: 100%)[
        #if it.has("body") [
          #strong[#it.supplement #context { it.counter.display(it.numbering) }] #it.body
        ]
      ]
    ]
  }

  // Outline (TOC) styling: Clean dotted leaders, robust inline layout without word-breaking columns
  show outline.entry: it => {
    let el = it.element
    let p-str = context {
      arm-page-number-string(el.location().page())
    }

    if el.func() == figure {
      // Figure or Table entry in List of Figures / List of Tables (R3-01 fix)
      let fig-num = context {
        let prefix = if el.kind == table or el.kind == "table" { "Table " } else { "Figure " }
        prefix + get-figure-number-string(el)
      }
      let cap-text = if el.caption != none { el.caption.body } else { el.supplement }

      v(3pt, weak: true)
      text(font: font-sans, size: 8.5pt, fill: arm-dark-gray)[
        #block(width: 100%)[
          #link(el.location())[
            #strong(fig-num) #h(6pt)
            #cap-text
          ]
          #box(width: 1fr, repeat(text(fill: arm-border-gray)[. ]))
          #h(6pt)
          #link(el.location())[#p-str]
        ]
      ]
      return
    }

    // Heading outline entries
    let num-str = if el.numbering != none {
      context {
        let count = counter(heading).at(el.location())
        let in-app = is-appendix.at(el.location())
        if el.level == 2 and in-app {
          "Appendix " + arm-heading-numbering(..count)
        } else {
          arm-heading-numbering(..count)
        }
      }
    } else {
      ""
    }

    if it.level == 1 {
      let is-gloss = to-string(el.body).contains("Glossary")
      if is-gloss {
        // Glossary in TOC: Has dotted leader and clickable page link (R3-07 fix)
        v(6pt, weak: true)
        text(font: font-sans, size: 9.5pt, weight: "bold", fill: arm-black)[
          #block(width: 100%)[
            #link(el.location())[#el.body]
            #box(width: 1fr, repeat(text(fill: arm-border-gray)[. ]))
            #h(6pt)
            #link(el.location())[#p-str]
          ]
        ]
        v(3pt, weak: true)
      } else {
        // Major Part Title in TOC (No page number per ARM standard)
        v(10pt, weak: true)
        text(font: font-sans, size: 10.5pt, weight: "bold", fill: arm-black)[
          #block(width: 100%)[
            #link(el.location())[
              #if num-str != "" [#num-str #h(8pt)]
              #el.body
            ]
          ]
        ]
        v(4pt, weak: true)
      }
    } else if it.level == 2 {
      // Chapter or Appendix entry in TOC
      v(4pt, weak: true)
      text(font: font-sans, size: 9pt, weight: "bold", fill: arm-black)[
        #block(width: 100%)[
          #link(el.location())[
            #if num-str != "" [#num-str #h(6pt)]
            #el.body
          ]
          #box(width: 1fr, repeat(text(fill: arm-border-gray)[. ]))
          #h(6pt)
          #link(el.location())[#p-str]
        ]
      ]
    } else {
      // Section entry in TOC
      v(2pt, weak: true)
      text(font: font-sans, size: 8.5pt, fill: arm-dark-gray)[
        #block(width: 100%)[
          #link(el.location())[
            #if num-str != "" [#num-str #h(6pt)]
            #el.body
          ]
          #box(width: 1fr, repeat(text(fill: arm-border-gray)[. ]))
          #h(6pt)
          #link(el.location())[#p-str]
        ]
      ]
    }
  }

  // Content page tracking for robust blank page suppression
  show par: it => it + metadata("page-content")
  show heading: it => it + metadata("page-content")
  show figure: it => it + metadata("page-content")
  show table: it => it + metadata("page-content")
  show raw.where(block: true): it => it + metadata("page-content")

  // Heading Styling: Part, Chapter, Section, Subsection
  // Implements User Requirement 1 (Chapter and A.B each start at top of new page)
  show heading: it => {
    let do-chapter-break() = {
      if recto {
        pagebreak(to: "odd", weak: true)
      } else {
        pagebreak(weak: true)
      }
    }

    if it.level == 1 {
      let is-glossary = to-string(it.body).contains("Glossary")
      if is-glossary {
        // Glossary Top-level Page: starts at top of page without huge gap
        do-chapter-break()
        pad(left: -gutter-width)[
          #text(font: font-sans, size: size-chap-title, weight: "bold", fill: arm-black)[
            #it.body
          ]
          #v(20pt)
        ]
      } else {
        // Part Title Page: starts on odd page if recto
        do-chapter-break()
        pad(left: -gutter-width)[
          // Vertically centered title presentation for Part divisor
          #v(140pt)
          #align(right)[
            #if it.numbering != none [
              #text(font: font-sans, size: size-part-num, weight: "bold", fill: arm-black)[
                #counter(heading).display(it.numbering)
              ]
              #v(12pt)
            ]
            #text(font: font-sans, size: size-part-title, weight: if it.numbering == none { "bold" } else { "regular" }, fill: if it.numbering == none { arm-black } else { arm-dark-gray })[
              #it.body
            ]
          ]
        ]
        pagebreak(weak: true)
      }
    } else if it.level == 2 {
      // Chapter or Appendix Start Page (User Requirement 1):
      // Starts on a new page directly at top margin (y ≈ 46-60pt), v(205pt) removed.
      do-chapter-break()
      counter(figure.where(kind: image)).update(0)
      counter(figure.where(kind: table)).update(0)
      pad(left: -gutter-width)[
        #align(left)[
          #context {
            let in-app = is-appendix.get()
            let prefix = if in-app { "Appendix " } else { "Chapter " }
            if it.numbering != none [
              #text(font: font-sans, size: size-chap-num, weight: "regular", fill: arm-black)[
                #prefix#counter(heading).display(it.numbering)
              ]
              #v(6pt)
            ]
          }
          #text(font: font-sans, size: size-chap-title, weight: "bold", fill: arm-black)[
            #it.body
          ]
        ]
        #v(18pt)
      ]
    } else if it.level == 3 {
      // Section Heading (A.B level):
      // User Requirement 1: Each A.B starts at top of a new page (next page, not recto odd).
      if section-pagebreak {
        pagebreak(weak: true)
      } else {
        v(16pt, weak: true)
      }
      pad(left: -gutter-width)[
        #grid(
          columns: (52pt, 1fr),
          gutter: 6pt,
          text(font: font-sans, size: size-sec, weight: "bold", fill: arm-black)[
            #if it.numbering != none {
              counter(heading).display(it.numbering)
            }
          ],
          text(font: font-sans, size: size-sec, weight: "bold", fill: arm-black)[
            #it.body
          ]
        )
      ]
      v(8pt)
    } else if it.level == 4 {
      // Subsection Heading (A.B.C level):
      // Stays within normal body flow (NO forced pagebreak).
      v(14pt, weak: true)
      pad(left: -gutter-width)[
        #grid(
          columns: (52pt, 1fr),
          gutter: 6pt,
          text(font: font-sans, size: size-subsec, weight: "bold", fill: arm-black)[
            #if it.numbering != none {
              counter(heading).display(it.numbering)
            }
          ],
          text(font: font-sans, size: size-subsec, weight: "bold", fill: arm-black)[
            #it.body
          ]
        )
      ]
      v(6pt, weak: true)
    } else {
      // Sub-subsection / minor heading: normal body flow
      v(10pt, weak: true)
      text(font: font-sans, size: size-subsubsec, weight: "bold", fill: arm-black)[
        #it.body
      ]
      v(4pt, weak: true)
    }
  }

  body
}
