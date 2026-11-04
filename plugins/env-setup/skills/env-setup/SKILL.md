---
name: env-setup
description: AI 코딩 에이전트 개발 환경을 구성한다. herdr(터미널 에이전트 멀티플렉서), rtk(토큰 절약 CLI 프록시)를 설치하고, claude 바이너리가 존재하는 경우 effortless 플러그인을 설치하며, Claude Code 및 Codex에 Serena MCP를 연결한다.
---

# 개발 환경 구성 (env-setup)

이 스킬은 AI 코딩 에이전트(Claude Code, Codex 등)를 위한 필수 개발 도구들을 설치하고 Serena MCP 서버를 연동합니다.

포함된 설정 항목:
1. **herdr**: Rust 기반 터미널 에이전트 멀티플렉서 (백그라운드 에이전트 감시 및 오케스트레이션)
2. **rtk (Rust Token Killer)**: LLM 토큰 소모를 줄여주는 CLI 프록시 설치 및 에이전트 훅 연동
3. **effortless**: (`claude` 바이너리가 존재하는 경우에만) Claude Code 추론 노력 및 캐싱 최적화 플러그인 설치
4. **Serena MCP**: Claude Code 및 Codex 환경에 시맨틱 심볼 분석 LSP 기반 Serena MCP 서버 등록

---

## 자동 설치 (권장)

스킬 루트 위치를 파악한 뒤 번들된 설치 스크립트를 실행합니다:

```bash
bash /path/to/skill/assets/setup.sh
```

스크립트는 필요한 도구들의 기설치 여부를 먼저 검사한 뒤 누락된 구성 요소만 순차적으로 설치하고 설정을 진행합니다.

---

## 단계별 수동 설치 절차

### 1. herdr 설치

터미널 멀티플렉서 `herdr`의 설치 여부를 확인하고 미설치 시 설치합니다.

```bash
# 설치 여부 확인
command -v herdr || curl -fsSL https://herdr.dev/install.sh | sh

# 대안 설치 (Homebrew 또는 Cargo)
# brew install herdr
# cargo install herdr

# 정상 설치 확인
herdr --version
```

### 2. rtk (Rust Token Killer) 설치 및 에이전트 연동

토큰 절약 프록시 `rtk`를 설치하고 사용할 코딩 에이전트에 초기화합니다.

```bash
# 설치 (바이너리는 ~/.local/bin 등에 위치)
command -v rtk || curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh

# PATH 확인 (~/.local/bin 포함 여부)
export PATH="${HOME}/.local/bin:${PATH}"

# 에이전트 글로벌 훅 등록
# Claude Code가 있는 경우:
rtk init -g

# Codex가 있는 경우:
rtk init -g --codex
```

### 3. effortless 플러그인 설치 (Claude Code 전용, 조건부)

시스템에 `claude` 바이너리가 존재하는지 먼저 확인합니다:

```bash
which claude
```

- **`claude` 바이너리가 존재하는 경우**:
  Claude Code 마켓플레이스를 추가하고 `effortless` 플러그인을 설치합니다.
  
  터미널에서 실행:
  ```bash
  claude plugin marketplace add HeyCubit/effortless
  claude plugin install effortless@effortless
  ```
  *(Claude Code 세션 안에서 실행할 때는 `/plugin marketplace add HeyCubit/effortless` 및 `/plugin install effortless@effortless` 사용)*

- **`claude` 바이너리가 없는 경우**:
  별도 설치를 진행하지 않고 건너뜁니다.

### 4. Serena MCP 서버 연결

시맨틱 코드 탐색을 위한 Serena MCP 서버를 각 에이전트에 등록합니다.

#### 사전 준비
`uv` 패키지 관리자가 설치되어 있어야 합니다:
```bash
command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Claude Code에 연결
`claude` 명령어가 있는 경우 사용자(user) 전역 범위로 Serena MCP를 추가합니다:
```bash
claude mcp add --scope user serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context claude-code
```
*(세션 내에서는 `/mcp add` 메뉴 또는 명령을 통해 동일하게 등록할 수 있습니다.)*

#### Codex에 연결
Codex CLI가 있는 경우:
```bash
codex mcp add serena -- uvx --from git+https://github.com/oraios/serena serena-mcp-server --context codex
```

CLI 명령을 지원하지 않는 경우 `~/.codex/config.toml`에 직접 추가합니다:
```toml
[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--context", "codex"]
```

---

## 설치 결과 확인

설치가 완료되면 다음 명령어로 환경 상태를 점검합니다:

```bash
herdr --version
rtk --version
# Claude Code MCP 상태 확인:
claude mcp list 2>/dev/null || true
# Codex MCP 상태 확인:
codex mcp list 2>/dev/null || true
```
