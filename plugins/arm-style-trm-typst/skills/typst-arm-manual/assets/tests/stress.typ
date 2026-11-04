// Neutral stress fixture
// Stress Test Document for ARM Architecture Reference Manual Typst Template
// Validates boundary conditions: multi-line headings, multi-page tables, wide figures,
// long code paths, forward/backward cross-references, odd/even recto transitions, and glossary.

#import "/template/lib.typ": *

#show: arm-doc.with(
  doc-info: (
    title: "ARM Architecture Reference Manual Template Boundary Stress Specification",
    subtitle: "경계 조건 검증용 종합 스트레스 테스트 문서 — 다중 파트 · 장문 제목 · 다중 페이지 분할 표 · 상호 참조 체계",
    product: "ARM Reference Architecture Template Validator",
    doc-id: "ARM-STRESS-TEST-001",
    issue-id: "ID999999",
    version: "2.5",
    issue: "Issue Z",
    date: "2026-11-03",
    author: "Template Verification Engineering Team",
    organization: "Template Verification Working Group (Sample)",
    confidentiality: "Non-Confidential — Stress Verification",
    copyright-short: "Copyright © 2026 Template Verification Team. All rights reserved.",
    product-status: "Draft Verification Suite (Stress Test Sample)",
    web-address: "https://example.com/arm-stress-template",
    history: (
      (date: "2026-11-01", issue: "A", confidentiality: "Non-Confidential", change: "Initial Draft (Sample Revision History)"),
      (date: "2026-11-02", issue: "B", confidentiality: "Non-Confidential", change: "Multi-page table splitting and long paths (Sample)"),
      (date: "2026-11-03", issue: "Z", confidentiality: "Non-Confidential", change: "Multi-line headings and cross-references (Sample)"),
    ),
    proprietary-text: [
      본 문서는 Typst 템플릿의 조판 및 한계 검증을 위해 인위적으로 작성된 스트레스 테스트 규격서입니다. 수록된 레지스터 데이터 및 아키텍처 수치는 *레이아웃 검증용 가상 예제*입니다.

      THIS DOCUMENT IS PROVIDED "AS IS" FOR TEMPLATE STRESS AND BOUNDARY VERIFICATION PURPOSES ONLY.
    ],
  ),
  paper: "arm-letter",
  recto: true,
  section-pagebreak: true, // User Requirement 1: Each A.B starts at top of a new page
  link-color: arm-blue,
  ref-italic: false,
)

// -------------------------------------------------------------------------
// Front Matter
// -------------------------------------------------------------------------

#cover-page()

#release-info-page()

#doc-admin-page(
  extra-notices: [
    #text(font: font-sans, weight: "bold")[검증 목적] \
    1. 두 줄 이상의 긴 제목이 TOC, 헤더, 본문에서 넘침 없이 조판되는지 검증
    2. 여러 페이지에 걸친 대형 표에서 머리글이 반복되는지 확인
    3. 본문 폭(411pt)을 초과하여 왼쪽 마진 영역(491.8pt)까지 확장되는 wide figure/table 동작 확인
    4. 동일 페이지, 다른 페이지, 전방, 후방 교차 참조 시 페이지 문구의 정확한 생성 및 생략 확인
  ],
)

#contents-page()

#list-of-figures()

#list-of-tables()

// Preface
#set heading(numbering: none)

== Preface <preface-stress>

=== About this stress document <sec-stress-about>
본 규격서는 ARM Architecture Reference Manual 조판 규칙을 엄격히 준수하면서, 시스템이 마주할 수 있는 극한의 텍스트 길이, 표 크기, 교차 참조 패턴을 검증합니다.

=== Conventions and link verification <sec-stress-conventions>
교차 참조 동작 사전 검증:
- 동일 페이지 참조: #arm-ref(<sec-stress-conventions>, form: "full") (현재 페이지이므로 "on page ..." 문구가 생략되어야 함).
- 먼 페이지 정방향 참조: #arm-ref(<sec-deep-backward-ref>, form: "full") (Part B 마지막 절을 가리키며 페이지 번호가 포함되어야 함).
- 특정 형식 테스트:
  - 절 번호만: #arm-ref(<sec-multi-line>, form: "num")
  - 절 제목만: #arm-ref(<sec-multi-line>, form: "title")
  - 번호 + 제목: #arm-ref(<sec-multi-line>, form: "num-title")
  - 페이지 번호만: #arm-ref(<sec-multi-line>, form: "page")

// -------------------------------------------------------------------------
// Part A: First Major Partition
// -------------------------------------------------------------------------

#set heading(numbering: arm-heading-numbering)
#counter(heading).update(0)

= Functional Architecture and Pipeline Semantics <part-func>

== Fundamental Processor Control Flow and Instruction Sequencing Model <ch-control-flow>
This chapter establishes the core pipeline state transitions, instruction fetch sequences, and verifies multi-line long title layout behavior.

It contains the following sections:
- #arm-ref(<sec-multi-line>, form: "full").
- #arm-ref(<sec-long-paths>, form: "full").

=== Architectural Execution Hierarchy with Excessively Long Multi-Line Heading Title for Header and Table of Contents Wrapping Verification <sec-multi-line>
이 절은 의도적으로 두 줄 이상으로 길게 늘려 쓴 제목입니다. 목차(TOC)와 페이지 상단 머리말(Header)에서 텍스트가 잘리거나 영역을 침범하지 않고 자연스럽게 줄바꿈되는지 검증합니다.

본문 내에서의 동일 절 상호 참조:
- #arm-ref(<sec-multi-line>, form: "full") (동일 페이지이므로 페이지 표기 생략).
- 원거리 정방향 참조: #arm-ref(<tbl-multi-page>, form: "full") (Chapter A2의 다중 페이지 분할 표로 연결).

#arm-note[
  긴 제목이 적용되었을 때 홀수/짝수 머리말의 정렬(`right` / `left`)과 줄 간격이 일정하게 유지되는지 확인하십시오.
]

=== Long System File Paths, Command Strings, and Deeply Nested Monospace Inline Blocks <sec-long-paths>
시스템 프로그래밍 환경에서는 디렉터리 경로와 빌드 플래그가 길어지는 경우가 빈번합니다.

긴 경로 표기 예시:
`src/subsystems/processing/controllers/scheduler/advanced_descriptor_queue_reorder_buffer_manager.cpp`

긴 터미널 명령 예시:
```bash
python3 run_simulation_cluster.py --gem5-binary=build/ARM/gem5.opt --config-script=configs/sample_multicore_topology.py --num-npu-tiles=8 --l2-cache-size=16MB --hbm-channels=8 --trace-rob-ticks --trace-active-loads --enable-cal-gap-verification --output-directory=results/cluster_runs/stress_experiment_2026_11_03_run_001
```

C++ 소스 코드 블록 검증:
```cpp
// 한국어 주석과 복합 템플릿 구문 검증
template <typename TData, size_t SPM_BANKS = 16>
class SampleReorderBuffer : public gem5::ClockedObject {
public:
    explicit SampleReorderBuffer(const SampleParams& params)
        : gem5::ClockedObject(params), activeLoadsCount(0), isStalled(false) {
        // 0x8FFF0000 메모리 맵 일관성 검사
        panic_if(params.baseAddress < 0x80000000, "잘못된 HBM 기저 주소 할당!");
    }

    void processCycle() {
        if (!isStalled && activeLoadsCount < MAX_CONCURRENT_LOADS) {
            scheduleNextDescriptorCommit();
        }
    }
private:
    uint32_t activeLoadsCount;
    bool isStalled;
};
```

== High-Density Data Layouts and Multi-Page Table Breaking <ch-tables-density>
This chapter exercises table layout mechanisms across page boundaries, ensuring header repetition and visual integrity.

It contains the following sections:
- #arm-ref(<sec-multi-page-table>, form: "full").
- #arm-ref(<sec-wide-figure>, form: "full").

=== Multi-Page Continuous Register Map Verification <sec-multi-page-table>
다음 표는 38개의 엔트리를 포함하여 의도적으로 두 개 이상의 페이지에 걸쳐 분할되도록 구성된 대형 레지스터 표입니다. 페이지가 넘어갈 때 표 머리글(`Address`, `Name`, `Type`, `Reset`, `Description`)이 반복되어야 하며, 상단에 ARM 스타일의 계속 캡션이 표시되어야 합니다.

#arm-table(
  table(
    columns: (1.5fr, 1.2fr, 0.8fr, 1.5fr, 3.5fr),
    stroke: (x, y) => (
      top: if y <= 1 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
      bottom: if y == 0 { 0.8pt + arm-black } else { 0.4pt + arm-border-gray },
      left: none,
      right: none,
    ),
    table.header(
      table-continuation-caption(<tbl-multi-page>, colspan: 5),
      [*Address*],
      [*Name*],
      [*Type*],
      [*Reset*],
      [*Description*],
    ),
    ..range(38).map(i => (
      table.cell(text(font: font-mono, size: size-table)[#("0x7000" + str(1000 + i * 4))]),
      table.cell(text(font: font-sans, size: size-table, weight: "bold")[#("STRESS_REG_" + str(i))]),
      table.cell(text(font: font-sans, size: size-table)[#(if calc.even(i) { "RW" } else { "RO" })]),
      table.cell(text(font: font-mono, size: size-table)[#("0x000000" + str(i))]),
      table.cell(text(font: font-serif, size: size-table)[#("Stress test simulated register entry number " + str(i) + " for multi-page split validation. Ensures table headers repeat properly across boundaries.")]),
    )).flatten()
  ),
  caption: [Summary of Extended Stress Test Registers Spanning Multiple Pages],
  label: <tbl-multi-page>,
  wide: true,
)

=== Wide Figure Spanning Beyond Normal Body Margin <sec-wide-figure>
#arm-ref(<fig-wide-test>, form: "full")은 기본 본문 폭(411pt)을 넘어 왼쪽 여백(491.8pt)까지 채우는 광폭 그림 예시입니다.

#arm-figure(
  grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 8pt,
    ..range(16).map(i => rect(width: 100%, height: 28pt)[#align(center + horizon)[Bank #i]]),
  ),
  caption: [Wide Multi-Bank SPM Memory Organization Spanning Full Printable Area],
  label: <fig-wide-test>,
  wide: true,
)

위 그림은 외부 이미지 파일 없이 생성한 가상의 16개 메모리 뱅크 배치 예시입니다.

// -------------------------------------------------------------------------
// Part B: Second Major Partition
// -------------------------------------------------------------------------

= Memory Hierarchy and Interface Architecture <part-mem>

== Cache Coherence, Memory Ordering and Barrier Primitives <ch-mem-order>
This chapter addresses memory barrier operations, store buffer draining, and cross-chapter reference validation.

It contains the following sections:
- #arm-ref(<sec-barrier-semantics>, form: "full").
- #arm-ref(<sec-bitfield-complex>, form: "full").
- #arm-ref(<sec-bitfield-long>, form: "full").

=== Memory Ordering and Hardware Synchronization Semantics <sec-barrier-semantics>
역방향 교차 참조 검증:
- 이전 파트의 첫 번째 절: #arm-ref(<sec-multi-line>, form: "full")
- 이전 챕터의 대형 표: #arm-ref(<tbl-multi-page>, form: "full")
- Preface의 표기 규약: #arm-ref(<sec-stress-conventions>, form: "full")
- 용어집 캐시 일관성 정의: #ref-glossary(<term-stress-coherence>)

#arm-caution[
  Store Buffer Flush 이전에는 비동기 DMA 완료 인터럽트가 발생하더라도 HBM 상의 데이터 가시성이 보장되지 않습니다. 반드시 메모리 배리어 명령을 선행하십시오.
]

=== Complex Multi-Bitfield Register Diagram <sec-bitfield-complex>
다음은 32비트 레지스터 내에 단일 비트 플래그, 4비트 필드, 예약 필드가 혼합된 복합 비트필드 다이어그램입니다 (#arm-ref(<fig-stress-barrier>, form: "full")).

#register-bitfield(
  caption: [STRESS_BARRIER_CTRL Bit Assignments (Layout Verification Virtual Example)],
  label: <fig-stress-barrier>,
  width: 32,
  fields: (
    (name: "DOMAIN", msb: 31, lsb: 28),
    (name: "Reserved", msb: 27, lsb: 24, reserved: true),
    (name: "TIMEOUT", msb: 23, lsb: 16),
    (name: "Reserved", msb: 15, lsb: 8, reserved: true),
    (name: "LEVEL", msb: 7, lsb: 4),
    (name: "FLUSH", msb: 3, lsb: 3),
    (name: "SYNC", msb: 2, lsb: 2),
    (name: "DRAIN", msb: 1, lsb: 1),
    (name: "EN", msb: 0, lsb: 0),
  ),
  descriptions: (
    (name: "DOMAIN", msb: 31, lsb: 28, description: [Coherency domain selector (0x1 = Inner Shareable, 0x2 = Outer Shareable, 0xF = System).]),
    (name: "TIMEOUT", msb: 23, lsb: 16, description: [Maximum clock cycles before raising a deadlock bus fault.]),
    (name: "LEVEL", msb: 7, lsb: 4, description: [Barrier severity level.]),
    (name: "FLUSH", msb: 3, lsb: 3, description: [Store queue flush request.]),
    (name: "SYNC", msb: 2, lsb: 2, description: [Full synchronous pipeline stall indicator.]),
    (name: "DRAIN", msb: 1, lsb: 1, description: [Write buffer drain signal.]),
    (name: "EN", msb: 0, lsb: 0, description: [Barrier module enable bit.]),
  )
)

=== High-Density 32-Bit Register with Extended Field Descriptions <sec-bitfield-long>
32개 단일 비트 필드와 복수 행에 걸친 긴 설명을 포함하는 고밀도 레지스터 다이어그램 검증 사례입니다 (#arm-ref(<fig-stress-long-fields>, form: "full")). 비트 다이어그램 자체는 원자적으로 유지되면서 설명 목록은 페이지 경계를 넘어 자연스럽게 분할되어야 합니다.

#register-bitfield(
  caption: [STRESS_EXT_STATUS Bit Assignments (Layout Verification Virtual Example)],
  label: <fig-stress-long-fields>,
  width: 32,
  fields: range(32).rev().map(i => (name: "F" + str(i), msb: i, lsb: i)),
  descriptions: range(32).rev().map(i => (
    name: "F" + str(i),
    msb: i,
    lsb: i,
    description: [This is a layout verification virtual example explaining a register field and its constraints in enough detail to wrap onto more than one line. 한글 필드 설명과 상태 전환 조건을 포함합니다.]
  )),
)

== Deep Reference and Edge Transition Verification <ch-edge-transitions>
This chapter validates cross-references to deep appendix locations and checks odd/even duplex page numbering continuity.

It contains the following sections:
- #arm-ref(<sec-deep-backward-ref>, form: "full").

=== Deep Cross-Reference Target and Forward Verification <sec-deep-backward-ref>
본 절은 교차 참조의 종착점 역할을 합니다:
- 본 절 자체의 동일 페이지 참조: #arm-ref(<sec-deep-backward-ref>, form: "full")
- 앞쪽 부록으로의 전방 참조: #arm-ref(<sec-appx-debug>, form: "full")
- 용어집 전체 참조: #arm-ref(<ch-stress-glossary>, form: "full")
- 용어집 개별 항목 참조: #ref-glossary(<term-stress-deadlock>)

#arm-warning[
  본 문서는 테스트 전용이므로 실제 하드웨어 설계 시에는 적용되지 않습니다.
]

// -------------------------------------------------------------------------
// Appendices
// -------------------------------------------------------------------------

= Appendices <part-stress-appx>
#start-appendix()

== Diagnostic and Fault Tolerant Test Hooks <ch-appx-debug>
This appendix outlines diagnostic exception vector tables and edge boundary recovery.

=== Debug Registers and Event Trace Vectors <sec-appx-debug>
시스템 디버깅 훅과 이벤트 카운터를 제공합니다.

#arm-note[
  진단 레지스터의 세부 비트 배치는 아키텍처 구현체마다 다를 수 있습니다.
]

== Batch Processing Limits and Concurrency Stalls <ch-appx-bench>
This appendix describes boundary conditions for queue overflow handling.

=== Batch Queue Overflow Recovery <sec-appx-batch>
큐 가득 참 상태에서의 백오프 알고리즘을 정의합니다.

// -------------------------------------------------------------------------
// Glossary
// -------------------------------------------------------------------------

#set heading(numbering: none)
= Glossary <ch-stress-glossary>

#glossary-entry("Cache Coherence", [다중 처리기 시스템에서 공유 메모리 데이터의 일관성을 유지하는 프로토콜.], label: <term-stress-coherence>)

#glossary-entry("Deadlock", [두 개 이상의 작업이 서로 상대방의 자원 해제를 기다리며 영구히 진행하지 못하는 교착 상태.], label: <term-stress-deadlock>)

#glossary-entry("Store Draining", [기록 버퍼에 보류된 데이터를 메모리 또는 하위 캐시로 완전히 방출하는 연산.], label: <term-stress-drain>)
