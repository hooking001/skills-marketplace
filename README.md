# hooking001 Skills Marketplace

Claude Code와 Codex에서 함께 사용하는 개인 스킬 모음입니다.

## 포함된 플러그인

| 플러그인 | 기능 |
| --- | --- |
| `serena-onboarding` | 프로젝트 구조와 실행 흐름을 분석해 Serena 메모리 작성·갱신 |
| `arm-style-trm-typst` | Typst로 ARM 형식 기술 매뉴얼 작성·빌드 |
| `cross-review` | 선택형 질문으로 범위·리뷰어 확인 후 독립 리뷰·상호 검토·최종 판정(Codex only / Codex + agy) |
| `env-setup` | herdr 설치, codex/claude 연동, Serena MCP 설정 |
| `nangate45` | Linux·macOS용 RTL 프로젝트 생성, Icarus 검증, Nangate45·사용자 Liberty 기반 Yosys 합성 |

플러그인 버전은 `.claude-plugin/marketplace.json`의 각 항목 `version`에서 관리합니다.

- `serena-onboarding`은 Serena MCP, Serena CLI, 언어별 language server가 필요합니다. 실행 시 프로젝트의 `.serena/`와 `.gitignore`를 생성하거나 갱신합니다.
- `nangate45`는 Python 3.8+, Bash, Yosys(ABC 포함), Icarus Verilog가 필요합니다. Nangate45 라이브러리를 포함하며 사용자 Liberty도 선택할 수 있습니다. [사용·검증 안내](plugins/nangate45/skills/nangate45/README.md)를 참고하세요. 기존 독립 `nangate45_skill` 저장소를 이 플러그인으로 통합했습니다.
- `env-setup`은 Claude Code가 설치되어 있으면 `effortless` 플러그인도 설치합니다.
- `cross-review`는 Codex + agy에서 독립 리뷰 후 서로의 지적에 동의·비동의와 근거를 제출하고 호스트가 최종 판정합니다. 문제 제기와 상대 검토 답변은 '관찰자'로 명시하며, 호스트 판정과 역할을 구분합니다. agy 호출 시 429 사용량 한도 초과 방지를 위해 Gemini Flash High(`gemini-3.8-flash-high`, `--effort high`)를 강제하며, 시스템 전체 동시 실행 agy는 최대 3개로 제한합니다. Codex 호스트 및 서브에이전트의 model·effort는 `~/.codex/config.toml`을 참조해 보고서에 명시합니다. 보고서는 두괄식으로 첫 줄에 1줄 핵심 문제와 1줄 해결책(수정방안)을 먼저 제시하고(문제 3줄·답변 10줄 이내), 작성 AI·model·effort를 병기하며 상세 근거는 기본으로 접습니다. agy의 최근 5분 진행 diff가 있으면 계속 대기합니다. 종료 시 최초 실행 디렉터리에 `cross-review-report-YYYYMMDD-HHMMSS.md`를 저장하고, 저장한 보고서를 다시 읽어 결과를 요약합니다.

## 설치

### Claude Code

Claude Code 세션에서 실행

```text
/plugin marketplace add https://github.com/hooking001/skills-marketplace.git
/plugin install {skills}@hooking001-skills
```

새 세션에서 스킬을 실행

```text
/serena-onboarding:serena-onboarding
/arm-style-trm-typst:typst-arm-manual
/env-setup:env-setup
/cross-review:cross-review
/nangate45:nangate45
```

### Codex

Codex 세션에서 실행

```text
!codex plugin marketplace add https://github.com/hooking001/skills-marketplace.git --ref main
!codex plugin add {skills}@hooking001-skills
```

새 세션에서 스킬 실행.

```
$serena-onboarding
$typst-arm-manual
$env-setup
$cross-review
$nangate45
```

## 구조

```text
.claude-plugin/marketplace.json      # 플러그인 목록과 버전
plugins/<plugin-name>/
  skills/<skill-name>/
    SKILL.md                        # 스킬 지침
    assets/                         # 템플릿, 스크립트 등
```

플러그인을 추가하려면 위 구조로 `SKILL.md`를 만들고 `marketplace.json`에 등록합니다. 별도의 `plugin.json`은 필요하지 않습니다.

`interface`는 Codex 전용 필드입니다. `claude plugin validate`에서 `Unknown field 'interface'` 경고가 나올 수 있으며, Claude Code는 이 필드를 무시합니다.

형식 참고: [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
