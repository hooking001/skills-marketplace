#import "/template/lib.typ": *
#let test-print = sys.inputs.at("print-mode", default: "false") == "true"
#show: arm-doc.with(print-mode: test-print, recto: false)
#set heading(numbering: arm-heading-numbering)

= Print Mode Test Section <sec-print-root>
== Links and Code Presentation <ch-print-ch1>
=== Section with Hyperlinks and Code <sec-print-content>

External hyperlink target: #link("https://example.com")[ExternalUrlLinkTarget]

Internal cross-reference target: #arm-ref(<sec-print-content>, form: "full")

```rust
fn execute_instruction(pc: u64, opcode: u32) -> Result<(), SimError> {
    // Monospace code block background and font retention test
    let target = pc + ((opcode as u64) << 2);
    Ok(())
}
```

Inline monospace sample: `sim_reg_read(0x4000)` test string.
