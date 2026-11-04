# hooking001 Skills Marketplace

Claude Code와 Codex에서 공용으로 사용하는 개인 스킬 마켓플레이스입니다.

설치 시 필요에 따라 저장소를 Private <-> Public으로 전환하여 운영하므로, 다른 머신에서 설치할 때 별도의 GitHub 인증(로그인, SSH 키, 토큰 등)을 준비할 필요 없이 세션 안에서 바로 설치할 수 있습니다.

## 포함된 플러그인

| 플러그인 | 기능 |
| --- | --- |
| `serena-onboarding` | 근거가 있는 코드 맵, 실행 흐름, 변경 가이드, 한국어 메모리와 캐시 검사 도구를 포함한 Serena 프로젝트 온보딩·갱신 |
| `arm-style-trm-typst` | ARM 형식 Typst 기술 매뉴얼 지침 (`typst-arm-manual`); 템플릿, 스크립트, 참고문서, 테스트 fixture, Pretendard 폰트 자산 전체 포함 |
| `env-setup` | herdr (codex/claude 연동), effortless (Claude 존재 시), Serena MCP 연결을 포함한 AI 코딩 환경 자동 구성 |

플러그인 버전은 `.claude-plugin/marketplace.json`의 각 항목 `version`에서 관리합니다.

- **환경 구성 (`env-setup`)**: 터미널 에이전트 멀티플렉서 `herdr`를 설치하고 `codex`, `claude` 인터그레이션을 연동하며, `claude` 바이너리가 존재하는 경우 `effortless` 플러그인을 설치하고, Claude Code와 Codex에 Serena MCP 서버를 연결합니다.
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
/plugin install env-setup@hooking001-skills
```

설치 후 새 세션에서 온보딩(`/serena-onboarding:serena-onboarding`), 기술 매뉴얼(`/arm-style-trm-typst:typst-arm-manual`), 환경 구성(`/env-setup:env-setup`)을 실행합니다.

### Codex

Codex 0.142.0 이상이 필요합니다(이 저장소는 Claude 형식 마켓플레이스 파일만 제공하며, Codex는 0.142.0부터 이를 플러그인 매니페스트로 사용합니다).

Codex 대화 세션 내 프롬프트에서 `!` 접두어를 사용하여 명령어를 실행하거나, `/plugins` 메뉴를 통해 대화형으로 설치합니다.

```text
!codex plugin marketplace add https://github.com/hooking001/skills-marketplace.git --ref main
!codex plugin add serena-onboarding@hooking001-skills
!codex plugin add arm-style-trm-typst@hooking001-skills
!codex plugin add env-setup@hooking001-skills
```

> **팁**: 대화 세션 안에서 `/plugins`를 입력하면 터미널 오버레이 브라우저가 열려 마켓플레이스 및 플러그인을 직접 확인하고 활성화/비활성화할 수도 있습니다.

설치 후 새 세션에서 `$serena-onboarding`, `$typst-arm-manual`, 또는 `$env-setup`을 지정하여 스킬을 호출합니다.

### 수동 복사 설치 (선택 사항)

플러그인 CLI를 지원하지 않는 환경에서는 저장소 클론 후 `plugins/<plugin-name>/skills/<skill-name>/` 디렉터리를 도구별 개인 스킬 디렉터리로 복사할 수 있습니다:
- Claude Code: `~/.claude/skills/<skill-name>/`
- Codex: `~/.agents/skills/<skill-name>/`

## 구조

Claude Code와 Codex가 하나의 마켓플레이스 파일과 하나의 스킬 원본을 공유합니다. 도구별 manifest(`.codex-plugin/`, `.agents/plugins/`, 플러그인별 `plugin.json`)는 두지 않습니다.

```text
.claude-plugin/marketplace.json      # 유일한 manifest: 플러그인 목록과 메타데이터(description, version, author, category, Codex interface)
plugins/<plugin-name>/
  skills/<skill-name>/
    SKILL.md                         # Claude Code와 Codex가 공유하는 단일 스킬 정의
    assets/                          # 스킬 자산 (템플릿, 스크립트, 폰트 등)
```

- **Claude Code**: `plugin.json`이 없는 플러그인은 `skills/`를 자동 탐색하고, 메타데이터는 마켓플레이스 항목에서 읽습니다.
- **Codex**: `.agents/plugins/marketplace.json`이 없으면 `.claude-plugin/marketplace.json`을 읽고, 플러그인 폴더에 manifest가 없으면 마켓플레이스 항목 필드로 manifest를 생성해 설치 캐시에 기록합니다(0.142.0 이상).
- `interface`는 Codex 전용 필드입니다. `claude plugin validate`가 `Unknown field 'interface'` 경고를 내지만 Claude Code는 로드 시 이 필드를 무시합니다.
- 플러그인을 추가할 때는 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`를 만들고 마켓플레이스 파일에 항목 하나만 추가합니다.

이 저장소는 스킬 배포용 파일만 포함하며, 머신별 인증 정보, Serena 프로젝트 캐시와 메모리, 전역 에이전트 설정은 포함하지 않습니다.

형식 참고: [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
