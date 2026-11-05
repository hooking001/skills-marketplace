# hooking001 Skills Marketplace

Claude Code와 Codex에서 함께 사용하는 개인 스킬 모음입니다.

## 포함된 플러그인

| 플러그인 | 기능 |
| --- | --- |
| `serena-onboarding` | 프로젝트 구조와 실행 흐름을 분석해 Serena 메모리 작성·갱신 |
| `arm-style-trm-typst` | Typst로 ARM 형식 기술 매뉴얼 작성·빌드 |
| `cross-review` | 대상 성격·범위를 확인한 뒤 문서·RTL·소스를 비판적으로 검토(Codex only / Codex + agy 선택) |
| `env-setup` | herdr 설치, codex/claude 연동, Serena MCP 설정 |

플러그인 버전은 `.claude-plugin/marketplace.json`의 각 항목 `version`에서 관리합니다.

- `serena-onboarding`은 Serena MCP, Serena CLI, 언어별 language server가 필요합니다. 실행 시 프로젝트의 `.serena/`와 `.gitignore`를 생성하거나 갱신합니다.
- `env-setup`은 Claude Code가 설치되어 있으면 `effortless` 플러그인도 설치합니다.

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
