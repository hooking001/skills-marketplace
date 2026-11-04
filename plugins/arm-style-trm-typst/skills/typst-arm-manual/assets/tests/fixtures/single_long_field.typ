#import "/template/lib.typ": *
#show: arm-doc.with(recto: false)
#set heading(numbering: arm-heading-numbering)
= Register Layout Test
== Register
=== Register Field Documentation
#register-bitfield(
  caption: [Long single field layout verification virtual example],
  width: 32,
  fields: ((name: "DATA", msb: 31, lsb: 0),),
  descriptions: ((name: "DATA", msb: 31, lsb: 0, description: [#lorem(900)]),),
)
