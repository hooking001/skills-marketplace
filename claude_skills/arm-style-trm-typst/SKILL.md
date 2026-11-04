---
name: typst-arm-manual
description: ARM 참조 매뉴얼 형식의 한영 기술 문서와 PDF를 Typst로 작성하거나 수정한다. 레지스터 비트필드, 여러 페이지 표, Part·Chapter·절 번호, 목차와 상호 참조가 필요한 기술 매뉴얼에 사용한다. Git 변경 이력을 정리하고 독립 reviewer 5명 중 3명 이상이 찬성한 중요한 변경만 기존 TRM에 반영한다.
---

# Typst ARM 기술 매뉴얼

이 파일이 있는 디렉터리를 스킬 루트로 삼는다. Codex와 Claude 모두 같은 `SKILL.md`와 상대 경로 자산을 사용한다. 특정 사용자 홈 경로나 전용 도구에 의존하지 않는다.

## 실행 모드와 Git 갱신

Git 프로젝트에서는 매 실행 기준 commit 또는 기준일부터의 log와 diff를 수집하여 추가·수정·삭제된 내용을 정리한다. 기존 TRM 갱신 및 Git 기반 최초 작성 시 [assets/references/git-review.md](assets/references/git-review.md)를 먼저 읽고 따른다. 기준과 소스 범위는 실행 간 보존한다.

기술 내용 수정은 독립 reviewer subagent **5명**을 실제로 호출하여 **후보별 찬성 3표 이상**을 얻은 경우에만 한다. 동시 실행 한도가 작으면 나누어 호출한다. 변경이 없거나 임계값을 넘은 후보가 없으면 TRM을 그대로 둔다. reviewer 의견·투표·결과는 TRM과 배포물에 넣지 않는다. 비 Git 자료의 최초 문서 작성은 아래 작성 절차를 사용한다.

## 문서 작성

1. 로드한 `SKILL.md`의 실제 위치에서 스킬 루트 절대 경로를 구한다. 현재 작업 폴더를 스킬 루트라고 가정하지 않는다. 아래 명령의 `/path/to/skill`은 그 실제 경로로 바꾼다. 출력 경로는 사용자의 현재 프로젝트 또는 요청한 위치를 기준으로 정한다.

   ```bash
   python3 /path/to/skill/assets/scripts/manual.py init /path/to/output/manual
   ```

   [assets/scripts/manual.py](assets/scripts/manual.py)의 `init` 명령은 새 폴더 또는 빈 폴더에 템플릿·폰트·시작 파일·빌드 스크립트를 복사한다. 기존 파일은 덮어쓰지 않는다. 기존 문서를 수정할 때는 필요한 자산만 선별해 반영한다. 설치된 스킬 자산은 출력 작업 공간으로 쓰지 않는다.
2. 복사한 `main.typ`의 문서 정보와 본문을 사용자 자료로 바꾼다. 기본 구조는 Part(`=`) → Chapter(`==`) → A.B 절(`===`) → A.B.C 항(`====`)이다. 전면부 이후 `#set heading(numbering: arm-heading-numbering)`을 유지한다.
3. 기능별 예제는 [assets/references/usage.md](assets/references/usage.md), 긴 표·비트필드·여러 Part 구성은 `assets/tests/stress.typ`를 참고한다. 예제 데이터는 모두 가상이며, 문서의 사실·메타데이터·이미지는 사용자의 자료로 작성한다.
4. 같은 도구의 `build` 명령으로 빌드한다. 어느 작업 디렉터리에서 실행해도 지정한 프로젝트의 `main.typ`를 빌드한다.

```bash
python3 /path/to/skill/assets/scripts/manual.py build /path/to/output/manual
# 필요하면 --entry main.typ --output build/manual.pdf를 지정한다.
```

생성된 프로젝트에는 독립 실행용 `build.sh`도 포함된다. 스킬이 없어도 `bash /path/to/output/manual/build.sh`로 빌드할 수 있다.

필요 도구는 Typst(기준 검증 버전 0.15.1)다. OS 전역 글꼴 설치는 필요 없다. 코드 글꼴은 Menlo → Courier New → Pretendard 순으로 선택하므로, 고정폭 표시가 필요하면 앞의 두 글꼴 중 하나가 환경에 있어야 한다. Pretendard의 `LICENSE`를 자산과 함께 보존한다. 폰트 무결성 확인과 재다운로드는 [assets/references/fonts.md](assets/references/fonts.md)를 참고한다.

## 설명에 필요한 다이어그램

구조·관계·동작을 글만으로 따라가기 어렵다면 적절한 다이어그램을 직접 작성해 해당 설명 가까이에 넣는다. 시스템/모듈 관계는 블록도, 명령·데이터 이동은 흐름도 또는 sequence diagram, 상태와 전이는 상태도, 주소 공간·버퍼·레이아웃은 메모리 배치도, 시간 관계가 중요하면 timing diagram을 선택한다. 모든 절에 의무적으로 그림을 추가하지 말고 독자의 이해를 개선하는 곳에 사용한다.

소스와 확인된 계약에 근거하여 방향·분기·주체·주소 공간·경계를 표시하고, 제안·미확정 사항은 구분한다. 근거 없는 연결·수치·timing을 그림으로 확정하지 않는다. 장식용 이미지를 구조 설명 대신 사용하지 않는다. 편집 가능한 Typst/SVG 등 벡터 방식과 프로젝트의 기존 도구를 우선하며, 의미가 있는 노드·화살표·연결선을 사용한다. 단순 텍스트 나열을 복잡한 구조의 블록도 대신 사용하지 않는다.

그림은 `arm-figure`로 감싸고 caption·label을 지정하여 본문에서 `arm-ref`로 연결한다. 원본 그림 소스도 프로젝트에 포함한다. connector 교차와 label 겹침을 줄이고, 최종 PDF에서 글자 크기·방향·범례·잘림을 확인한다. 기존 TRM의 그림 추가·변경도 Git 갱신 후보로 검토하여 위의 3/5 기준을 적용한다.

## 유지할 조판 규칙

- Chapter와 A.B는 각각 새 페이지의 본문 상단에서 시작하고, A.B.C는 본문 흐름을 유지한다. Chapter 제목 위에 큰 공백을 넣지 않는다.
- 기본 본문은 Pretendard 10pt, `body-leading: 0.75em`, `par-spacing: 1.2em`이다. 연속 줄 간격은 기본 검증 fixture에서 약 14.6pt이며 14–16pt를 기준으로 확인한다. 페이지 수를 줄이기 위해 간격을 압축하지 않는다.
- 전면부는 소문자 로마 숫자, 본문은 Chapter ID와 문서 전체 누적 물리 페이지를 결합한 번호를 쓴다. Chapter마다 페이지 번호를 1로 리셋하지 않는다.
- Part·표지·빈 페이지는 머리말/꼬리말을 억제한다. 새 절 시작 페이지의 러닝 헤더에는 그 절을 표시한다.
- 그림·표는 `arm-figure`, `arm-table`, 참조는 `arm-ref`를 사용한다. 라벨은 해당 컴포넌트의 `label:` 인자로 전달한다. 번호와 페이지를 수동 입력하지 않는다.
- 긴 표는 `table.header`로 머리글을 반복하고 필요하면 `table-continuation-caption`을 사용한다. 표 전체를 분할 불가능한 블록으로 감싸지 않는다.
- 비트필드는 `register-bitfield`를 사용한다. 모든 비트를 중복·누락 없이 정의한다. 도식은 한 덩어리로 유지하되 필드 설명은 여러 페이지로 분할할 수 있어야 한다.

세부 치수와 지원 옵션을 바꾸거나 레이아웃을 수정할 때 [assets/references/style.md](assets/references/style.md)를 읽는다. 사용자가 명시적으로 지정한 문서 요구는 이 기본값보다 우선한다.

## 확인 및 인계

새 문서는 경고·미해결 참조·내용 잘림을 확인하고, PDF를 렌더링하거나 뷰어로 열어 제목 시작, 표 경계, 긴 설명, 머리말/꼬리말을 확인한다. 빌드 성공만으로 육안 검수 완료를 보고하지 않는다.

임의의 완성 PDF는 다음 명령으로 검사할 수 있다. 현재 작업 폴더와 무관하게 전달한 PDF를 검사한다. 링크 구조, 북마크 대상, 물리 페이지 밖 텍스트, 미해결 참조 후보를 확인하며 내용의 사실성과 링크의 의미상 올바른 대상은 별도로 확인한다.

```bash
python3 /path/to/skill/assets/scripts/manual.py check /path/to/output/manual/build/manual.pdf
```

템플릿 자체를 변경했다면 `test` 명령을 실행한다. 중립적인 스트레스 예제와 `assets/tests/fixtures/`로 회귀 검사하며, 임시 작업 공간은 자동 삭제된다. 고정 페이지 수나 검증 결과를 새 사용자 문서에 적용하지 않는다.

```bash
python3 /path/to/skill/assets/scripts/manual.py test
```

검사에는 Python의 `pypdf`, `pdfplumber`가 필요하다(`assets/scripts/requirements.txt`). PDF 이미지 확인에는 Poppler의 `pdftoppm`을 사용할 수 있다. GUI 링크 클릭은 실제 수행하지 않았다면 미검증으로 보고한다.

현재 템플릿의 동적 페이지 번호는 기준 Typst 버전에서 PDF `/PageLabels`를 생성하지 않는다. 문서 안의 번호와 PDF 뷰어 입력창의 물리 페이지 번호가 다를 수 있다. 펌웨어·시뮬레이션·하드웨어 성능은 문서 조판 검사의 범위가 아니다.

최종 인계는 편집 가능한 Typst 프로젝트와 빌드된 PDF를 포함한다. 임시 렌더, 캐시, 검증 사본은 결과물 폴더에 남기지 않는다.
