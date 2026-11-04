# 조판 기본값과 구현 경계

아래 `template/` 경로는 생성된 프로젝트 루트(번들에서는 스킬 루트의 `assets/project/`)를 기준으로 한다. 도구와 검사 자료 경로는 스킬 루트를 기준으로 한다. ARM 참조 매뉴얼에서 착안한 조판 기본값이며 특정 제품이나 저장소의 자료는 필요하지 않다.

## 치수와 글꼴

| 항목 | 기본값 |
|---|---|
| 용지 `paper: "arm-letter"` | 595 × 792pt |
| 용지 `paper: "a4"` | 595.28 × 841.89pt |
| 왼쪽 번호 거터 시작 | 51.7pt |
| 본문 왼쪽 시작 | 132.5pt |
| 오른쪽 여백 | 53pt |
| 위 / 아래 여백 | 46 / 60pt |
| 전폭 콘텐츠 폭 (arm-letter) | 490.3pt |
| 꼬리말 괘선 (arm-letter) | y=750pt, 0.5pt 두께 |
| 본문 | Pretendard 10pt |
| 연속 줄 간격 | 기본 본문 fixture 약 14.6pt, 검사 기준 14–16pt; 모든 줄의 고정값이 아님 |
| Part / Chapter 제목 | 24 / 20pt |
| A.B / A.B.C 제목 | 12 / 10.5pt |
| 표 / 캡션 / 코드 | 8.5 / 9 / 8.5pt |
| 머리말 / 꼬리말 | 8pt |
| 표 셀 inset | x=6pt, y=5pt |
| 링크 | `#1212cc`; `print-mode: true`이면 검정 |

Pretendard v1.3.9 정적 OTF 9종을 제공한다. PDF에는 실제 사용된 가중치의 글리프 서브셋이 내장되며 모든 폰트 파일이 통째로 내장되는 것은 아니다. 코드용 Menlo/Courier New는 번들에 없으며 시스템에서 찾는다. Pretendard 정적 OTF의 small caps와 italic은 합성 처리된다. `smallcaps-term`은 ASCII 영문에만 적용한다.

## 페이지와 번호

`arm-doc` 기본 옵션은 `recto: true`, `section-pagebreak: true`, `body-size: 10pt`, `body-leading: 0.75em`, `par-spacing: 1.2em`이다. `recto`는 Part/Chapter를 홀수 면에 배치하며 필요한 짝수 빈 면을 만든다. `recto: false`는 그 빈 면 삽입을 해제한다. `section-pagebreak: false`는 A.B의 강제 페이지 나눔을 해제한다.

Chapter/A.B는 정상 본문 상단(기준 fixture 약 y=44–55pt)에 시작한다. 원본 ARM의 Chapter 제목은 약 y=250pt에 시작하지만 이 템플릿은 가독성과 사용자 요구에 맞춰 상단 배치를 채택했다. A.B.C는 본문 흐름을 따른다.

전면부는 Preface까지 로마 숫자를 사용한다. 본문 번호는 `A1-13`처럼 Chapter ID와 누적 물리 면을 결합한다. `#start-appendix()`는 이후 Chapter를 부록으로 전환한다. 독립 Glossary는 최상위 목차 항목과 `Glossary-<물리 면>` 꼬리말을 갖는다.

그림·표 번호는 대상이 위치한 Chapter를 기준으로 계산한다. 캡션·목록·참조·계속 캡션 모두 같은 대상 라벨을 사용해야 한다. `arm-ref`는 같은 면의 참조에서 불필요한 페이지 문구를 생략한다.

## 관련 구현

- `template/lib.typ`: 진입점 `arm-doc`, 옵션, `start-appendix`.
- `template/page.typ`: 치수, 머리말, 꼬리말, Part·빈 면 억제.
- `template/typography.typ`: 글꼴, 색상, 간격 상수.
- `template/numbering.typ`: Chapter·페이지·그림·표 번호.
- `template/frontmatter.typ`: 표지, 개정 이력, 문서 관리, 목차, 그림/표 목록.
- `template/components.typ`: 전폭 그림·표, 경고, 비트필드, 용어집.
- `template/crossref.typ`: 스마트 참조 `arm-ref`.

비트필드의 도식과 캡션은 분할하지 않는다. 설명 목록은 figure 밖에 두고, 각 필드 제목과 첫 설명 줄을 붙이되 긴 설명 자체는 페이지를 넘길 수 있게 한다. 러닝 헤더는 현재 면의 첫 A.B를 우선하고 없으면 같은 Chapter의 이전 활성 절을 사용한다.

`assets/scripts/manual.py test`는 `assets/tests/`의 예제와 fixture의 번호·링크 목적지·잘림·표 행 보존·페이지 이동·인쇄 색상·양면 배치를 검사한다. 특정 fixture의 성공을 모든 입력 PDF에 대한 보증으로 확대하지 않는다. GUI 클릭과 `/PageLabels` 제한은 [SKILL.md](../../SKILL.md)의 인계 지침을 따른다.
