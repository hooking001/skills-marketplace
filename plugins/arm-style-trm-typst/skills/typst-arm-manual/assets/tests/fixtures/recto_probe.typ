#import "/template/lib.typ": *
#let test-recto = sys.inputs.at("recto", default: "true") == "true"
#let test-paper = sys.inputs.at("paper", default: "arm-letter")
#show: arm-doc.with(paper: test-paper, recto: test-recto)
#set heading(numbering: arm-heading-numbering)

= Part One <part-1>
== Chapter One <ch-1>
=== Section 1.1 <sec-1-1>
Short section body on first chapter.

== Chapter Two <ch-2>
=== Section 2.1 <sec-2-1>
Short section body on second chapter.

= Part Two <part-2>
== Chapter Three <ch-3>
=== Section 3.1 <sec-3-1>
Short section body on third chapter under Part Two.
