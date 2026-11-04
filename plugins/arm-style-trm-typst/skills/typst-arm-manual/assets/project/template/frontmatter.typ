// template/frontmatter.typ
// Front matter layout components: Cover, Release Info, Document Admin, Contents, Lists of Figures/Tables

#import "typography.typ": *
#import "page.typ": gutter-width, printable-width
#import "numbering.typ": arm-heading-numbering
#import "crossref.typ": doc-link-color

// Document state to store metadata from arm-doc
#let doc-info-state = state("doc-info-state", (:))

// 1. Cover Page
#let cover-page(
  title: none,
  subtitle: none,
  doc-id: none,
  confidentiality: none,
  date: none,
  copyright: none,
) = context {
  let info = doc-info-state.get()
  let d-title = if title != none { title } else { info.at("title", default: "Technical Reference Manual") }
  let d-subtitle = if subtitle != none { subtitle } else { info.at("subtitle", default: "") }
  let d-id = if doc-id != none { doc-id } else { info.at("doc-id", default: "") }
  let d-conf = if confidentiality != none { confidentiality } else { info.at("confidentiality", default: "Non-Confidential") }
  let d-date = if date != none { date } else { info.at("date", default: "") }
  let d-copy = if copyright != none { copyright } else { info.at("copyright-short", default: "Copyright © 2026. All rights reserved.") }

  // Suppress header and footer on the cover
  pad(left: -gutter-width)[
    // Top whitespace bringing title block down matching ARM standard
    #v(140pt)
    #align(right)[
      #block(width: 440pt)[
        #text(font: font-sans, size: size-doc-title, weight: "bold", fill: arm-black)[
          #d-title
        ]
        #if d-subtitle != "" [
          #v(16pt)
          #text(font: font-sans, size: 14pt, weight: "medium", fill: arm-dark-gray)[
            #d-subtitle
          ]
        ]
      ]
    ]

    #v(1fr)

    // Bottom metadata block
    #align(center)[
      #block(width: 100%)[
        #if d-id != "" [
          #text(font: font-sans, size: 11pt, weight: "bold", fill: arm-black)[#d-id] \
          #v(4pt)
        ]
        #text(font: font-sans, size: 9pt, fill: arm-muted-gray)[#d-conf] \
        #if d-date != "" [
          #v(2pt)
          #text(font: font-sans, size: 8.5pt, fill: arm-muted-gray)[#d-date] \
        ]
        #v(4pt)
        #text(font: font-sans, size: 8pt, fill: arm-muted-gray)[#d-copy]
      ]
    ]
    #v(20pt)
  ]
  pagebreak(weak: true)
}

// 2. Release Information Page (Change History & Proprietary Notice)
#let release-info-page(
  history: none,
  notice: none,
) = context {
  let info = doc-info-state.get()
  let d-hist = if history != none { history } else { info.at("history", default: ()) }
  let d-notice = if notice != none { notice } else { info.at("proprietary-text", default: [
    This document is confidential and proprietary. An illustrative sample notice for template evaluation.
  ]) }

  pad(left: -gutter-width)[
    #text(font: font-sans, size: 14pt, weight: "bold", fill: arm-black)[Release Information]
    #v(4pt)
    #text(font: font-sans, size: 8pt, fill: arm-muted-gray)[Change History (Illustrative sample metadata)]
    #v(10pt)

    #if d-hist.len() > 0 [
      #table(
        columns: (1fr, 1fr, 1.8fr, 3.2fr),
        stroke: (x, y) => (
          top: if y <= 1 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
          bottom: if y == 0 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
          left: none,
          right: none,
        ),
        table.header(
          [*Date*],
          [*Issue*],
          [*Confidentiality*],
          [*Change*],
        ),
        ..d-hist.map(h => (
          table.cell(text(font: font-sans, size: 8pt)[#h.at("date", default: "")]),
          table.cell(text(font: font-sans, size: 8pt)[#h.at("issue", default: "")]),
          table.cell(text(font: font-sans, size: 8pt)[#h.at("confidentiality", default: "")]),
          table.cell(text(font: font-serif, size: 8pt)[#h.at("change", default: "")]),
        )).flatten()
      )
    ]

    #v(24pt)
    #text(font: font-sans, size: 11pt, weight: "bold", fill: arm-black)[Proprietary Notice]
    #v(6pt)
    #block(
      width: 100%,
      text(font: font-serif, size: 8.5pt, fill: arm-dark-gray)[#d-notice]
    )
  ]
  pagebreak(weak: true)
}

// 3. Document Administration Page
#let doc-admin-page(
  org: none,
  prod-status: none,
  web: none,
  extra-notices: none,
) = context {
  let info = doc-info-state.get()
  let d-org = if org != none { org } else { info.at("organization", default: "Architecture Working Group (Sample)") }
  let d-status = if prod-status != none { prod-status } else { info.at("product-status", default: "Platform Specification (Sample)") }
  let d-web = if web != none { web } else { info.at("web-address", default: "https://example.com/technical-manual") }
  let d-extra = if extra-notices != none { extra-notices } else { none }
  let link-color = doc-link-color.get()

  pad(left: -gutter-width)[
    #text(font: font-sans, size: 14pt, weight: "bold", fill: arm-black)[Document Administration]
    #v(10pt)

    #block(text(font: font-serif, size: 9pt)[
      #text(weight: "bold")[Organization / Publisher] \
      #d-org
      #v(8pt)
      #text(weight: "bold")[Product Status] \
      #d-status
      #v(8pt)
      #text(weight: "bold")[Web Address (Sample Link)] \
      #link(d-web)[#text(font: font-mono, fill: link-color)[#d-web]]
    ])

    #if d-extra != none [
      #v(20pt)
      #d-extra
    ]
  ]
  pagebreak(weak: true)
}

// 4. Custom Contents Page
#let contents-page() = {
  metadata((kind: "frontmatter-section", title: "Contents"))
  pad(left: -gutter-width)[
    #v(20pt)
    #text(font: font-sans, size: size-chap-title, weight: "bold", fill: arm-black)[Contents]
    #v(20pt)
  ]

  // Typst outline configured with ARM styling
  outline(
    title: none,
    depth: 3,
    indent: 14pt,
  )
  pagebreak(weak: true)
}

// 5. Optional List of Figures
#let list-of-figures(title: "List of Figures") = {
  metadata((kind: "frontmatter-section", title: title))
  pad(left: -gutter-width)[
    #v(20pt)
    #text(font: font-sans, size: 16pt, weight: "bold", fill: arm-black)[#title]
    #v(16pt)
  ]
  outline(
    title: none,
    target: figure.where(kind: image),
  )
  pagebreak(weak: true)
}

// 6. Optional List of Tables
#let list-of-tables(title: "List of Tables") = {
  metadata((kind: "frontmatter-section", title: title))
  pad(left: -gutter-width)[
    #v(20pt)
    #text(font: font-sans, size: 16pt, weight: "bold", fill: arm-black)[#title]
    #v(16pt)
  ]
  outline(
    title: none,
    target: figure.where(kind: table),
  )
  pagebreak(weak: true)
}
