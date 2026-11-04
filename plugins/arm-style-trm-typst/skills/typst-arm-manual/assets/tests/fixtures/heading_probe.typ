#import "/template/lib.typ": *
#show: arm-doc.with(recto: false)
#set heading(numbering: arm-heading-numbering)
= Architecture <probe-part>
== Pipeline <probe-ch>
Chapter introduction.
=== First Section <probe-sec>
This is a deliberately repeated English and Korean mixed paragraph. 한글 문장과 English words 사이의 간격을 검토합니다. This paragraph is long enough to wrap onto several lines so that real consecutive baseline distances can be measured independently of any paragraph gaps. 읽기 쉬운 줄 간격을 확보하고 실제 PDF의 연속 줄 위치를 측정합니다.
==== First Subsection <probe-sub1>
Short text under the first subsection.
==== Second Subsection <probe-sub2>
Short text under the second subsection.
=== Second Section <probe-sec2>
Another section.
#context [#metadata(query(heading).map(h => (level: h.level, title: to-string(h.body), page: h.location().page(), y: h.location().position().y / 1pt))) <probe-headings>]
