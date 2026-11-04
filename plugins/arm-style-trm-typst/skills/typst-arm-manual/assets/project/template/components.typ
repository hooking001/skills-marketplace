// template/components.typ
// Reusable components: callouts, wide blocks, register tables, register bitfields, glossary

#import "typography.typ": *
#import "page.typ": gutter-width, printable-width
#import "numbering.typ": get-figure-number-string

// 1. Wide Block
// Expands content into the left gutter (full printable width)
#let wide-block(body) = {
  pad(left: -gutter-width, body)
}

// 2. Callouts (Note, Caution, Warning)
// Technical reference style matching armv7m_arm.pdf
#let arm-note(body, title: "Note") = {
  block(
    width: 100%,
    above: 1.2em,
    below: 1.2em,
    [
      #set text(font: font-sans, size: size-subsec, weight: "bold", fill: arm-black)
      #title
      #v(3pt)
      #block(
        inset: (left: 0pt),
        [
          #set text(font: font-serif, size: size-body, weight: "regular", fill: arm-black)
          #body
        ]
      )
    ]
  )
}

#let arm-caution(body, title: "Caution") = {
  block(
    width: 100%,
    above: 1.2em,
    below: 1.2em,
    [
      #set text(font: font-sans, size: size-subsec, weight: "bold", fill: rgb("#b30000"))
      #title
      #v(3pt)
      #block(
        inset: (left: 0pt),
        [
          #set text(font: font-serif, size: size-body, weight: "regular", fill: arm-black)
          #body
        ]
      )
    ]
  )
}

#let arm-warning(body, title: "Warning") = {
  block(
    width: 100%,
    above: 1.2em,
    below: 1.2em,
    [
      #set text(font: font-sans, size: size-subsec, weight: "bold", fill: rgb("#c45100"))
      #title
      #v(3pt)
      #block(
        inset: (left: 0pt),
        [
          #set text(font: font-serif, size: size-body, weight: "regular", fill: arm-black)
          #body
        ]
      )
    ]
  )
}

// 3. Figures with ARM-style caption placement (below figure, right-aligned)
// Directly attaches label to the inner figure to ensure semantic integrity in cross-referencing.
#let arm-figure(
  content,
  caption: none,
  label: none,
  wide: false,
) = {
  let inner = figure(
    content,
    caption: if caption != none { figure.caption(position: bottom, caption) } else { none },
    kind: image,
    supplement: [Figure],
  )
  let labeled = if label != none {
    [#inner #label]
  } else {
    inner
  }
  if wide {
    wide-block(labeled)
  } else {
    labeled
  }
}

// 4. Tables with ARM-style caption placement (above table, right-aligned)
// Directly attaches label to the inner figure, ensuring crossref receives figure rather than pad.
#let arm-table(
  content,
  caption: none,
  label: none,
  wide: true,
) = {
  let inner = figure(
    content,
    caption: if caption != none { figure.caption(position: top, caption) } else { none },
    kind: table,
    supplement: [Table],
  )
  let labeled = if label != none {
    [#inner #label]
  } else {
    inner
  }
  if wide {
    wide-block(labeled)
  } else {
    labeled
  }
}

// Helper: Reusable Continuation Caption Cell for multi-page breakable tables
#let table-continuation-caption(target-label, colspan: 1) = {
  table.cell(colspan: colspan, stroke: none)[
    #context {
      let cur = here().page()
      let matches = query(target-label)
      if matches.len() > 0 {
        let el = matches.first()
        if cur > el.location().page() {
          let fig-num = get-figure-number-string(el)
          let cap-text = if el.caption != none { el.caption.body } else { "" }
          align(right)[#text(font: font-sans, size: size-caption, weight: "bold")[Table #fig-num #cap-text (continued)]]
        }
      }
    }
  ]
}

// 5. Register Bitfield Diagram (32-bit, 16-bit, 64-bit, or custom width)
// Validates bit ranges, order, missing/overlapping bits, and wraps inside a real figure.
// Bit index row and register box row are wrapped in an atomic, non-breakable block to prevent splitting (R3-02).
#let register-bitfield(
  caption: none,
  label: none,
  width: 32,
  fields: (),
  descriptions: none,
  wide: false,
) = {
  // Validate width
  assert(type(width) == int and width > 0, message: "register-bitfield: width must be a positive integer, got " + repr(width))
  assert(fields.len() > 0, message: "register-bitfield: fields list cannot be empty")

  // Validate fields and range completeness
  let covered-bits = ()
  for (idx, f) in fields.enumerate() {
    assert("msb" in f and "lsb" in f, message: "register-bitfield field at index " + str(idx) + " is missing 'msb' or 'lsb': " + repr(f))
    let msb = f.msb
    let lsb = f.lsb
    assert(type(msb) == int and type(lsb) == int, message: "register-bitfield msb and lsb must be integers in field: " + repr(f))
    assert(msb >= lsb, message: "register-bitfield: msb must be >= lsb in field: " + repr(f) + " (msb=" + str(msb) + ", lsb=" + str(lsb) + ")")
    assert(msb < width, message: "register-bitfield: msb " + str(msb) + " exceeds register width " + str(width) + " in field: " + repr(f))
    assert(lsb >= 0, message: "register-bitfield: lsb " + str(lsb) + " is negative in field: " + repr(f))

    for b in range(lsb, msb + 1) {
      assert(not covered-bits.contains(b), message: "register-bitfield: bit " + str(b) + " is duplicated or overlapping across fields!")
      covered-bits.push(b)
    }
  }

  // Ensure all bits from 0 to width - 1 are covered
  assert(covered-bits.len() == width, message: "register-bitfield: bitfield coverage mismatch! Covered " + str(covered-bits.len()) + " of " + str(width) + " bits.")

  // Ensure contiguous descending order
  assert(fields.first().msb == width - 1, message: "register-bitfield: highest field must start at msb=" + str(width - 1))
  assert(fields.last().lsb == 0, message: "register-bitfield: lowest field must end at lsb=0")
  for idx in range(fields.len() - 1) {
    let cur = fields.at(idx)
    let nxt = fields.at(idx + 1)
    assert(cur.lsb == nxt.msb + 1, message: "register-bitfield: fields must be contiguous and ordered descending by bit position. Discontinuity between " + repr(cur) + " and " + repr(nxt))
  }

  // Column fraction by bit width
  let cols = fields.map(f => (f.msb - f.lsb + 1) * 1fr)

  // Find if any 1-2 bit fields have text labels that need vertical rotation
  let has-narrow-rotated = fields.any(f => {
    let span = f.msb - f.lsb + 1
    let name = f.at("name", default: "")
    span <= 2 and name.len() > 2 and not f.at("reserved", default: false)
  })
  let box-height = if has-narrow-rotated { 54pt } else { 28pt }

  // Atomic diagram: Indices and boxes are strictly non-breakable (R3-02)
  let diagram-box = block(
    width: 100%,
    breakable: false,
    [
      // Top Bit Indices Row
      #grid(
        columns: cols,
        gutter: 0pt,
        ..fields.map(f => {
          let span = f.msb - f.lsb + 1
          let bit-str = if span == 1 {
            str(f.msb)
          } else {
            str(f.msb) + h(1fr) + str(f.lsb)
          }
          align(center + bottom)[
            #text(font: font-sans, size: size-bit-idx, fill: arm-muted-gray)[#bit-str]
          ]
        })
      )
      #v(2pt)

      // Box Row
      #grid(
        columns: cols,
        gutter: 0pt,
        ..fields.map(f => {
          let span = f.msb - f.lsb + 1
          let is-res = f.at("reserved", default: false)
          let name = f.at("name", default: if is-res { "Reserved" } else { "" })
          let bg = if is-res { arm-res-gray } else { white }
          let is-narrow = span <= 2 and name.len() > 2 and not is-res

          rect(
            width: 100%,
            height: box-height,
            fill: bg,
            stroke: 0.6pt + arm-black,
            radius: 0pt,
            inset: 1pt,
            align(center + horizon)[
              #set text(
                font: font-sans,
                size: if is-narrow { 6pt } else { size-bit-name },
                weight: if is-res { "regular" } else { "bold" },
                fill: if is-res { arm-muted-gray } else { arm-black },
              )
              #if is-narrow [
                #rotate(-90deg, reflow: true)[#name]
              ] else if is-res [
                #if span >= 3 [ Reserved ] else [ - ]
              ] else [
                #name
              ]
            ]
          )
        })
      )
    ]
  )

  // Atomic diagram figure (R4-04 fix):
  // Bit index row and register box row are wrapped in an atomic, non-breakable block inside figure.
  // Caption, label, and figure counter are strictly bound to this atomic diagram figure.
  let fig = figure(
    diagram-box,
    caption: if caption != none { figure.caption(position: bottom, caption) } else { none },
    kind: image,
    supplement: [Figure],
  )

  let labeled = if label != none {
    [#fig #label]
  } else {
    fig
  }

  let rendered-fig = if wide {
    wide-block(labeled)
  } else {
    labeled
  }

  // Field descriptions (R4-04 fix):
  // Separated outside the non-breakable figure into normal body flow,
  // allowing descriptions to break across page boundaries naturally without truncation.
  // Each field item is an atomic block to keep field title and initial text together.
  let desc-content = if descriptions != none {
    [
      #metadata("content-start")
      #block(
        width: 100%,
        above: 1.0em,
        below: 0.8em,
        [
          #for desc in descriptions {
            let range-str = if desc.msb == desc.lsb {
              "bit[" + str(desc.msb) + "]"
            } else {
              "bits[" + str(desc.msb) + ":" + str(desc.lsb) + "]"
            }
            block(
              width: 100%,
              above: 0.6em,
              below: 2pt,
              sticky: true,
              breakable: false,
              align(left)[
                #metadata("page-content")
                #text(font: font-sans, size: size-body, weight: "bold", fill: arm-black)[#desc.name, #range-str]
              ]
            )
            block(
              width: 100%,
              above: 0pt,
              below: 0.6em,
              inset: (left: 12pt),
              breakable: true,
              align(left)[
                #set text(font: font-serif, size: size-body, fill: arm-dark-gray)
                #desc.description
              ]
            )
          }
        ]
      )
      #metadata("content-end")
    ]
  } else {
    none
  }

  [#rendered-fig#desc-content]
}

// 6. Summary Register Table
#let register-summary-table(
  caption: none,
  label: none,
  registers: (),
  wide: true,
) = {
  let content = table(
    columns: (1.5fr, 1.2fr, 0.8fr, 1.5fr, 3.5fr),
    stroke: (x, y) => (
      top: if y <= 1 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
      bottom: if y == 0 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
      left: none,
      right: none,
    ),
    table.header(
      [*Address*],
      [*Name*],
      [*Type*],
      [*Reset*],
      [*Description*],
    ),
    ..registers.map(r => (
      table.cell(text(font: font-mono, size: size-table)[#r.address]),
      table.cell(text(font: font-sans, size: size-table, weight: "bold")[#r.name]),
      table.cell(text(font: font-sans, size: size-table)[#r.type]),
      table.cell(text(font: font-mono, size: size-table)[#r.reset]),
      table.cell(text(font: font-serif, size: size-table)[#r.description]),
    )).flatten()
  )

  arm-table(content, caption: caption, label: label, wide: wide)
}

// 7. Interactive Glossary Entry Component
#let glossary-entry(
  term,
  body,
  label: none,
) = {
  let anchor = if label != none {
    [#metadata((kind: "glossary", term: term)) #label]
  } else {
    none
  }

  block(
    width: 100%,
    above: 1.0em,
    below: 1.0em,
    [
      #anchor
      #text(font: font-sans, size: size-sec, weight: "bold", fill: arm-black)[#term]
      #v(3pt)
      #block(
        inset: (left: 0pt),
        [
          #set text(font: font-serif, size: size-body, fill: arm-dark-gray)
          #body
        ]
      )
    ]
  )
}
