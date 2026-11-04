#import "/template/lib.typ": *
#show: arm-doc.with(recto: false)
#set heading(numbering: arm-heading-numbering)
= Register Layout Validation
== Full Register
=== Field Descriptions
#register-bitfield(
  caption: [Long field description layout verification virtual example],
  width: 32,
  fields: range(32).rev().map(i => (name: "F" + str(i), msb: i, lsb: i)),
  descriptions: range(32).rev().map(i => (name: "F" + str(i), msb: i, lsb: i, description: [This is a layout verification virtual example explaining a register field and its constraints in enough detail to wrap onto more than one line. 한글 필드 설명과 상태 전환 조건을 포함합니다.])),
  label: <long-fields>,
)
