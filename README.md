# hooking001 Skills Marketplace

Claude Code와 Codex에서 공용으로 사용하는 개인 스킬 마켓플레이스입니다.

설치 시 필요에 따라 저장소를 Private <-> Public으로 전환하여 운영하므로, 다른 머신에서 설치할 때 별도의 GitHub 인증(로그인, SSH 키, 토큰 등)을 준비할 필요 없이 세션 안에서 바로 설치할 수 있습니다.

## 포함된 플러그인

| 플러그인 | 버전 | 기능 |
| --- | --- | --- |
| `serena-onboarding` | `0.1.0` | 근거가 있는 코드 맵, 실행 흐름, 변경 가이드, 한국어 메모리와 캐시 검사 도구를 포함한 Serena 프로젝트 온보딩·갱신 |
| `arm-style-trm-typst` | `0.2.0` | ARM 형식 Typst 기술 매뉴얼 지침 (`typst-arm-manual`); 템플릿, 스크립트, 참고문서, 테스트 fixture, Pretendard 폰트 자산 전체 포함 |

- **Serena 온보딩**: Serena MCP를 대상 도구에 미리 연결해야 합니다. 언어별 분석에는 해당 language server가 필요하며, 인덱싱에는 설치된 Serena CLI를 사용합니다. 이 플러그인은 Serena나 language server를 자동 설치하지 않습니다. 스킬을 실행하면 대상 프로젝트의 `.serena/` 파일과 이를 제외하는 `.gitignore` 규칙을 생성하거나 갱신할 수 있습니다.
- **ARM 기술 매뉴얼**: 템플릿, `manual.py` 자동화 스크립트, Pretendard 글꼴, 회귀 테스트 fixture 등 문서 작성·빌드·검사에 필요한 자산이 `assets/`에 온전히 포함되어 있습니다.

## 세션 내 설치 방법

저장소를 일시적으로 Public으로 전환한 상태라면 GitHub 인증 설정 없이 대화 세션 안에서 바로 설치할 수 있습니다.

### Claude Code

Claude Code 세션 프롬프트에서 아래 명령어를 순서대로 실행합니다.

```text
/plugin marketplace add https://github.com/hooking001/skills-marketplace.git
/plugin install serena-onboarding@hooking001-skills
/plugin install arm-style-trm-typst@hooking001-skills
```

설치 후 새 세션에서 `/serena-onboarding:serena-onboarding` 또는 `/arm-style-trm-typst:typst-arm-manual`을 실행합니다.

### Codex

Codex 대화 세션 내 프롬프트에서 `!` 접두어를 사용하여 명령어를 실행하거나, `/plugins` 메뉴를 통해 대화형으로 설치합니다.

```text
!codex plugin marketplace add https://github.com/hooking001/skills-marketplace.git --ref main
!codex plugin add serena-onboarding@hooking001-skills
!codex plugin add arm-style-trm-typst@hooking001-skills
```

> **팁**: 대화 세션 안에서 `/plugins`를 입력하면 터미널 오버레이 브라우저가 열려 마켓플레이스 및 플러그인을 직접 확인하고 활성화/비활성화할 수도 있습니다.

설치 후 새 세션에서 `$serena-onboarding` 또는 `$typst-arm-manual`을 지정하여 스킬을 호출합니다.

### 수동 복사 설치 (선택 사항)

플러그인 CLI를 지원하지 않는 환경에서는 저장소 클론 후 `plugins/<plugin-name>/skills/<skill-name>/` 디렉터리를 도구별 개인 스킬 디렉터리로 복사할 수 있습니다:
- Claude Code: `~/.claude/skills/<skill-name>/`
- Codex: `~/.agents/skills/<skill-name>/`

## 구조

스킬은 Claude Code와 Codex용으로 별도 디렉터리를 나누지 않고, 단일 스킬 원본으로 통합 관리됩니다.

```text
.claude-plugin/marketplace.json       # Claude Code 마켓플레이스 등록 정보
.agents/plugins/marketplace.json      # Codex 마켓플레이스 등록 정보
plugins/<plugin-name>/
  .claude-plugin/plugin.json          # Claude Code manifest
  .codex-plugin/plugin.json           # Codex manifest
  skills/<skill-name>/
    SKILL.md                         # Claude Code와 Codex가 공유하는 단일 스킬 정의
    assets/                          # 스킬 자산 (템플릿, 스크립트, 폰트 등)
```

이 저장소는 스킬 배포용 파일만 포함하며, 머신별 인증 정보, Serena 프로젝트 캐시와 메모리, 전역 에이전트 설정은 포함하지 않습니다.

형식 참고: [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
