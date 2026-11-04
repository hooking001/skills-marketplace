# API 및 사용 예제

예제의 경로는 생성된 프로젝트 루트를 기준으로 한다. 첫 예제는 `main.typ`로 사용할 수 있고, 이후 컴포넌트 예제는 같은 문서의 본문에 넣는다. 문서 정보와 레지스터 값은 가상 예시이므로 실제 자료로 교체한다.

## 기본 문서

```typst
#import "template/lib.typ": *

#show: arm-doc.with(
  doc-info: (
    title: "My Architecture Specification",
    subtitle: "Hardware Model and Firmware Interface",
    product: "Platform 1.0",
    doc-id: "MY-DOC-001",
    issue-id: "DRAFT",
    version: "1.0",
    issue: "Issue A",
    author: "My Engineering Team",
    confidentiality: "Non-Confidential",
    copyright-short: "Sample document — replace metadata before delivery.",
  ),
  paper: "arm-letter",       // 595x792 pt (기본) 또는 "a4"
  recto: true,               // Chapter/Part 홀수 페이지 시작
  section-pagebreak: true,   // Chapter 및 A.B 절 새 페이지 상단 시작
  body-size: 10pt,           // 본문 크기 10pt
  body-leading: 0.75em,      // 실제 연속 줄 간격 ~14.6pt
)

// 전면부 (Front Matter)
#cover-page()
#release-info-page()
#doc-admin-page()
#contents-page()

// 본문 계층 번호 활성화
#set heading(numbering: arm-heading-numbering)

= Application Architecture <part-app>

== Core Pipeline Overview <ch-pipeline>
This chapter describes the pipeline control flow.

=== Execution Units <sec-exec-units>
The execution unit details are described in #arm-ref(<tbl-regs>, form: "full").

#arm-table(
  table(
    columns: (1fr, 1fr, 2fr),
    table.header([*Address*], [*Name*], [*Description*]),
    [0x00], [CTRL], [Control register],
    [0x04], [STATUS], [Status register],
  ),
  caption: [Summary of Pipeline Control Registers],
  label: <tbl-regs>,
)
```

---

## 컴포넌트 API

### 스마트 상호 참조 (`arm-ref`)

대상 라벨(`label`)의 위치를 동적으로 감지하여 시맨틱 번호와 클릭 링크를 자동 생성합니다. 대상이 동일 페이지에 있으면 페이지 표기를 생략하고, 다른 페이지에 있으면 `"on page ..."`를 자동으로 덧붙입니다.

```typst
#arm-ref(<target>, form: "full", italic: false)
```

- `form: "full"` (기본값): 대상이 **동일 페이지**에 있으면 `Section A1.1 Overview`만 출력하고, **다른 페이지**에 있으면 `Section A1.1 Overview on page A1-14`처럼 페이지 문구를 자동 추가합니다.
- `form: "num"`: 절/그림/표 번호만 출력 (예: `A1.1`, `Figure A1-1`, `Table B1-1`).
- `form: "title"`: 대상 제목 텍스트만 출력.
- `form: "num-title"`: 번호와 제목 출력 (예: `Section A1.1 Overview`).
- `form: "page"`: 대상의 인쇄 페이지 문자열만 출력 (예: `A1-14`, `ii`).

### 32비트 레지스터 비트필드 다이어그램 (`register-bitfield`)

32비트 레지스터 구조를 시각화하고 완전한 비트 범위(MSB~LSB)와 누락·중복을 엄격히 검증하는 정규 `figure` 컴포넌트입니다. 인덱스 번호 행과 박스는 단일 비분할(atomic) 블록으로 결합되어 페이지 경계에서 갈라지지 않으며, 상세 필드 설명(`descriptions`)은 figure 외부의 일반 본문 블록으로 분리됩니다.
각 필드 설명 항목은 `sticky: true`를 적용하여 **필드 제목과 첫 설명 줄의 결합을 보장**하며, 한 필드의 설명이 한 페이지를 초과하는 장문(예: 900단어)인 경우에도 설명 단락이 페이지 경계를 넘어 자연스럽게 분할되어 하단 잘림이나 꼬리말 침범 없이 조판됩니다.

```typst
#register-bitfield(
  caption: [Command and Control Register (CMD_CTRL) bit assignments],
  width: 32,
  fields: (
    (name: "Reserved", msb: 31, lsb: 24, reserved: true),
    (name: "QUEUE_ID", msb: 23, lsb: 16),
    (name: "Reserved", msb: 15, lsb: 12, reserved: true),
    (name: "PRIORITY", msb: 11, lsb: 8),
    (name: "Reserved", msb: 7,  lsb: 3,  reserved: true),
    (name: "IRQ_EN",   msb: 2,  lsb: 2),
    (name: "ABORT",    msb: 1,  lsb: 1),
    (name: "START",    msb: 0,  lsb: 0),
  ),
  descriptions: (
    (name: "QUEUE_ID", msb: 23, lsb: 16, description: [Target hardware queue identifier.]),
    (name: "PRIORITY", msb: 11, lsb: 8,  description: [Queue priority tier (0x0=lowest, 0xF=highest).]),
    (name: "IRQ_EN",   msb: 2,  lsb: 2,  description: [Interrupt enable flag.]),
    (name: "ABORT",    msb: 1,  lsb: 1,  description: [Abort active command.]),
    (name: "START",    msb: 0,  lsb: 0,  description: [Write 1 to trigger command execution.]),
  ),
  label: <fig-cmd-ctrl>,
)
```

### 다중 페이지 분할 표 및 계속 캡션 (`table-continuation-caption`)

대형 표가 여러 페이지로 분할될 때 머리글 반복과 함께 계속 캡션을 손쉽게 추가할 수 있는 표준 API를 제공합니다.

```typst
#arm-table(
  table(
    columns: (1fr, 2fr),
    table.header(
      table-continuation-caption(<my-large-table>, colspan: 2),
      [*Key*], [*Value*],
    ),
    [0x00], [Control register],
    [0x04], [Status register],
  ),
  caption: [My Large Multi-Page Table],
  label: <my-large-table>,
)
```

---

## 폰트와 조판 설정

기본 본문은 Pretendard 10pt, `body-leading: 0.75em`이다. 기본 본문 fixture에서 연속 줄 간격은 약 14.6pt이며, 글꼴·크기·문단 내용에 따라 달라진다. 제목·표·코드에는 역할별 크기를 적용한다.

폰트 제공 범위와 무결성 검사·갱신 명령은 [fonts.md](fonts.md), 전체 치수·번호·페이지 나눔 규칙은 [style.md](style.md)를 참고한다.
