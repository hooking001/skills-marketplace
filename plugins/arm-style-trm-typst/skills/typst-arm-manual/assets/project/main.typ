#import "template/lib.typ": *

#show: arm-doc.with(
  doc-info: (
    title: "Technical Reference Manual",
    subtitle: "기술 참조 매뉴얼",
    product: "Sample Product",
    doc-id: "SAMPLE-TRM-001",
    issue-id: "DRAFT",
    version: "0.1",
    issue: "Draft",
    author: "Sample Team",
    organization: "Sample Organization",
    confidentiality: "Draft — Sample",
    copyright-short: "Sample document — replace metadata before delivery.",
  ),
  paper: "arm-letter",
  recto: true,
  section-pagebreak: true,
)

#cover-page()
#contents-page()
#list-of-tables()

#set heading(numbering: arm-heading-numbering)

= Architecture <part-architecture>

== Overview <chapter-overview>
이 문서는 재사용 가능한 기술 매뉴얼 시작 파일입니다. 제품 정보와 본문을 실제 자료로 교체하세요.

=== Interface <section-interface>
레지스터 요약은 #arm-ref(<table-registers>, form: "full")를 참조하세요.

#arm-table(
  table(
    columns: (1fr, 1fr, 2fr),
    table.header([*Offset*], [*Register*], [*Description*]),
    [0x00], [CONTROL], [Illustrative control register],
  ),
  caption: [Sample register map],
  label: <table-registers>,
)

==== Control Register <subsection-control>
아래 비트필드는 사용 예시이며 실제 하드웨어 사양이 아닙니다.

#register-bitfield(
  caption: [Sample CONTROL register],
  label: <figure-control>,
  width: 32,
  fields: (
    (name: "Reserved", msb: 31, lsb: 1, reserved: true),
    (name: "EN", msb: 0, lsb: 0),
  ),
  descriptions: (
    (name: "EN", msb: 0, lsb: 0, description: [Example enable flag.]),
  ),
)
