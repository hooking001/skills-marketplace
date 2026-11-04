#import "/template/lib.typ": *
#show: arm-doc.with(
  doc-info: (title: "Delta Shift Test", doc-id: "SHIFT-01"),
  paper: "arm-letter",
  recto: false,
)
#contents-page()
#list-of-tables()

// Controlled 2-page dummy insertion in front
#pagebreak()
Dummy Page Shift 1
#pagebreak()
Dummy Page Shift 2

#set heading(numbering: arm-heading-numbering)
= Part A <part-a>
== Chapter A1 <ch-a1>
=== Section A1.1 <sec-a1-1>
Reference to target table: #arm-ref(<tbl-target>, form: "full")

== Chapter A2 <ch-a2>
=== Section A2.1 <sec-a2-1>
#arm-table(
  table(columns: 2, [Col A], [Col B]),
  caption: [Target Delta Table],
  label: <tbl-target>,
)
