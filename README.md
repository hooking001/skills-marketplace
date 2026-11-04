# hooking001 Skills Marketplace

Claude Code와 Codex에서 사용하는 개인 스킬 모음입니다. 이 저장소는 Private으로 운영하며, 설치하는 머신마다 저장소 읽기 권한과 GitHub 인증이 필요합니다.

## 포함된 플러그인

| 플러그인 | 버전 | 기능 |
| --- | --- | --- |
| `serena-onboarding` | `0.1.0` | 근거가 있는 코드 맵, 실행 흐름, 변경 가이드, 한국어 메모리와 캐시 검사 도구를 포함한 Serena 프로젝트 온보딩·갱신 |
| `arm-style-trm-typst` | `0.1.0` | ARM 형식 Typst 기술 매뉴얼 지침 (`typst-arm-manual`); 현재 SKILL.md만 포함 |

Serena MCP를 대상 도구에 미리 연결해야 합니다. 언어별 분석에는 해당 language server가 필요하며, 인덱싱에는 설치된 Serena CLI를 사용합니다. 이 플러그인은 Serena나 language server를 자동 설치하지 않습니다. 스킬을 실행하면 대상 프로젝트의 `.serena/` 파일과 이를 제외하는 `.gitignore` 규칙을 생성하거나 갱신할 수 있습니다.

## 도구별 스킬 원본과 자산 상태

`claude_skills/`와 `codex_skills/`에 각각 `serena-onboarding/`과 `arm-style-trm-typst/`를 포함합니다. Serena 원본은 원격 머신의 각 도구별 디렉터리에서 복사했고, ARM 스킬은 원격 홈의 `arm-style-trm-typst/`에서 두 도구용으로 복사했습니다. 플러그인의 스킬 파일은 이 원본과 동일합니다.

**ARM 스킬은 현재 불완전한 배포본입니다.** 제공된 원본에는 `SKILL.md`만 있으며, 여기서 참조하는 `assets/scripts/manual.py`, 템플릿, 참고문서, 테스트 fixture, 폰트와 라이선스가 없습니다. 전체 assets를 보완하기 전에는 이 스킬에 설명된 문서 초기화·빌드·PDF 검사 절차를 실행할 수 없습니다. 이 저장소는 누락된 파일을 임의로 생성하지 않습니다. 내부 스킬 이름 `typst-arm-manual`은 원본 그대로 유지했습니다.

직접 복사 설치 시 Claude Code는 원하는 디렉터리를 `~/.claude/skills/`로, Codex는 `~/.agents/skills/`로 복사합니다. ARM 스킬은 내부 이름에 맞춰 `typst-arm-manual/`로 설치합니다. 기존 설치를 먼저 비교하고, marketplace 설치와 중복되지 않도록 한 방식을 선택하세요.

## 다른 머신에서 설치

먼저 GitHub 인증을 준비합니다. HTTPS를 사용하는 아래 예제는 `gh` CLI를 사용할 경우 다음과 같이 설정할 수 있습니다. 이미 유효한 Git credential helper가 있다면 기존 인증을 사용해도 됩니다.

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
git ls-remote https://github.com/hooking001/skills-marketplace.git HEAD
```

토큰을 remote URL에 넣거나 저장소에 기록하지 마세요.

### Claude Code

Claude Code 세션에서 실행합니다.

```text
/plugin marketplace add https://github.com/hooking001/skills-marketplace.git
/plugin install serena-onboarding@hooking001-skills
/plugin install arm-style-trm-typst@hooking001-skills
```

설치 후 새 세션에서 `/serena-onboarding:serena-onboarding`을 실행하거나 Serena 온보딩을 요청합니다. 동일한 스킬이 로컬 skills 디렉터리에 이미 설치되어 있다면 중복 실행을 피하도록 사용할 설치본을 확인하세요.

### Codex

`codex plugin` 명령을 지원하는 버전에서 실행합니다.

```bash
codex plugin marketplace add https://github.com/hooking001/skills-marketplace.git --ref main
codex plugin add serena-onboarding@hooking001-skills
codex plugin add arm-style-trm-typst@hooking001-skills
```

ARM 스킬 호출 이름은 Claude Code의 `/arm-style-trm-typst:typst-arm-manual`, Codex의 `$typst-arm-manual`입니다. 위 자산 상태를 확인한 후 사용하세요.

설치 후 새 세션에서 `$serena-onboarding`을 지정해 온보딩을 요청합니다. 플러그인 CLI를 지원하지 않는 버전에서는 인증된 clone을 만든 뒤, `plugins/serena-onboarding/skills/serena-onboarding/` 디렉터리를 Codex의 개인 스킬 경로 `~/.agents/skills/serena-onboarding/`로 복사할 수 있습니다. 기존 설치가 있으면 먼저 비교하여 사용자 변경을 보존하세요.

## 다른 머신에서 스킬 추가

```bash
git clone https://github.com/hooking001/skills-marketplace.git
cd skills-marketplace
git switch main
git pull --ff-only
```

1. `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`와 필요한 assets를 추가합니다. 스킬에서 사용하는 상대경로를 유지합니다.
2. 기존 플러그인을 참고하여 `.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json`을 플러그인 디렉터리 안에 추가합니다. 두 manifest의 이름·버전과 `skills` 경로를 맞춥니다.
3. 루트의 `.claude-plugin/marketplace.json`과 `.agents/plugins/marketplace.json`에 같은 플러그인을 등록합니다. source 경로는 각 JSON 파일의 디렉터리가 아닌 **저장소 루트 기준**입니다.
4. 해당 스킬의 `claude_skills/`, `codex_skills/` 복사본도 함께 갱신하여 플러그인과 내용이 일치하게 유지합니다. README의 플러그인 목록과 자산 상태를 갱신하고 검증 후 커밋·push합니다.

```bash
claude plugin validate .
claude plugin validate ./plugins/<plugin-name>
git add README.md .claude-plugin/marketplace.json .agents/plugins/marketplace.json plugins/<plugin-name>
git commit -m "Add <plugin-name> skill plugin"
git push origin main
```

다른 머신의 push로 충돌하면 원격 변경을 먼저 통합하고 다시 검증합니다. 강제 push는 사용하지 않습니다. 기존 플러그인을 변경할 때는 두 manifest의 버전도 함께 올립니다.

## 구조

```text
claude_skills/<skill-dir>/          # Claude Code용 스킬 복사본
codex_skills/<skill-dir>/           # Codex용 스킬 복사본
.claude-plugin/marketplace.json       # Claude Code 목록
.agents/plugins/marketplace.json      # Codex 목록
plugins/<plugin-name>/
  .claude-plugin/plugin.json          # Claude Code manifest
  .codex-plugin/plugin.json           # Codex manifest
  skills/<skill-name>/
    SKILL.md                         # 두 도구가 공유하는 스킬
    assets/                          # 필요한 경우 포함
```

이 저장소는 스킬 배포용 파일만 포함합니다. 머신별 인증 정보, Serena 프로젝트 캐시와 메모리, 전역 에이전트 설정은 포함하지 않습니다.

형식 참고: [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
