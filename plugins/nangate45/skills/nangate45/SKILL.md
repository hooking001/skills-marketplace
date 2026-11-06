---
name: nangate45
description: Nangate45 또는 지정한 Liberty 라이브러리로 Verilog RTL을 Yosys 표준 셀에 매핑하고 면적·셀 통계를 산출한다. Icarus 시뮬레이션과 Linux·macOS용 독립 RTL 프로젝트 생성에도 사용한다. 배치배선·STA·전력 분석은 포함하지 않는다.
---

# Liberty 기반 RTL 합성과 검증

Nangate45 typical을 기본으로 사용한다. 다른 공정·코너는 사용자가 제공한 Liberty를 명시적으로 선택한다. 이 스킬의 경로는 현재 작업 디렉터리가 아니라 **이 SKILL.md가 있는 디렉터리**를 기준으로 해석한다.

## 작업 선택

- **새 프로젝트**: `bash <skill>/scripts/setup_project.sh <name> [parent] [--top <module>] [--liberty <file>]`. 이름과 top은 단순 Verilog 식별자여야 한다. 기존 경로를 덮어쓰지 않는다. 생성된 프로젝트는 라이브러리와 실행 코드를 복사하므로 스킬 이동·삭제 이후에도 동작한다.
- **기존 RTL 합성**: 사용자의 프로젝트 구조를 먼저 확인한다. 생성기가 기존 RTL을 덮어쓰게 하지 말고 별도 작업 디렉터리를 만든 뒤 `script/rtl.f`, `project.json`을 실제 설계에 맞춘다. 사용자가 선택한 top과 라이브러리를 보존한다.
- **예제 확인**: `bash <skill>/example/full_adder_4bit/run_all.sh`. Icarus의 512개 전수 검사 후 Yosys 합성을 수행하며, 어느 단계든 실패하면 실패로 종료한다.

## 실행 계약

Python 3.8+, Bash, Yosys(ABC 포함), Icarus Verilog(`iverilog`, `vvp`)를 PATH에서 찾는다. 다운로드 시에만 curl이 필요하다. 고정된 Homebrew 경로를 추가하거나 패키지를 자동 설치하지 않는다. 실행 파일 경로는 `YOSYS`, `IVERILOG`, `VVP` 환경변수로 지정할 수 있다.

생성 프로젝트의 `project.json`은 `top`, `tb_top`, `liberty`를 지정한다. Liberty 경로는 프로젝트 루트 기준이다. `script/rtl.f`, `script/tb.f`는 한 줄에 소스 파일 경로 하나를 기록하고 각 파일리스트의 위치를 기준으로 상대 경로를 해석한다. 공백 경로·빈 줄·CRLF·전체 줄 `#`/`//` 주석을 지원한다. 옵션, glob, 중첩 파일리스트, 인라인 주석은 지원하지 않는다. 옵션이나 복잡한 SystemVerilog 기능이 필요한 설계는 기존 빌드 시스템을 사용하거나 실행기를 명시적으로 확장한다. Yosys 기본 프런트엔드의 SystemVerilog 지원은 제한적이다.

```bash
bash <project>/script/run_tb.sh                  # project.json의 tb_top
bash <project>/script/run_synth.sh               # project.json의 top과 liberty
bash <project>/script/run_synth.sh other_top --liberty lib/other_corner.lib
bash <project>/script/run_tb.sh other_top --tb-top other_top_tb
bash <project>/clean.sh
```

실행 위치는 자유롭다. 시뮬레이션 cwd는 `script/`이므로 테스트벤치 파형은 `../dump/<top>.vcd`에 기록한다. top을 바꾸면 테스트벤치도 함께 지정한다. `clean.sh`는 실행기가 기록한 출력만 지우며 임의의 파형 경로는 추적하지 않는다.

## 합성 결과 판단

실행기는 `synth -flatten -noabc` → `dfflibmap` → `abc` → 라이브러리 셀 로드 → `check -mapped -assert` → `stat -liberty` 순서로 매핑과 구조 검사를 수행한다. 미매핑 내부 셀·잘못된 연결은 성공으로 보고하지 않는다. 실패한 재실행에서는 이전 넷리스트를 제거한다.

- `synth/<top>_synth.v`: 매핑 넷리스트
- `synth/<top>_synth_report.txt`: 전체 도구 로그와 최종 셀 통계
- `synth/synth_<top>.ys`: 재현 가능한 Yosys 명령

보고할 때 도구 버전, top, 소스 목록, 사용한 Liberty·코너를 확인한다. 로그 중간의 일반 합성 통계가 아니라 **마지막 Liberty 기반 통계**를 사용한다. 셀 수는 논리 게이트 환산치가 아니며, 면적은 Liberty의 셀 면적 합계다. Nangate45에서는 µm²로 해석하지만 임의 라이브러리의 단위는 확인해야 한다. 이 결과로 타이밍 충족, 실제 배치 면적, 전력 또는 RTL-넷리스트 등가성을 단정하지 않는다. 게이트 시뮬레이션에는 Liberty가 아닌 별도 Verilog 셀 모델이 필요하다.

## 라이브러리 복구 및 상세 안내

`bash <skill>/scripts/download_nangate45.sh [directory]`는 [고정 커밋·SHA-256 목록](resources/library.json)으로 세 자산을 검증한다. 누락 파일만 임시 파일로 내려받아 검증 후 배치한다. 기존 파일의 해시가 다르면 보존하고 실패하므로 원인을 확인한 뒤 별도 디렉터리로 복구한다. 네트워크 접근 없이 포함 자산을 사용할 수 있다.

플랫폼 준비, 설치, 지원 범위와 검증 방법은 [README.md](README.md)를 필요한 경우 참조한다. 자산 출처와 원본 라이선스는 [resources/PROVENANCE.md](resources/PROVENANCE.md), [resources/NANGATE-LICENSE](resources/NANGATE-LICENSE)에 보존되어 있다.
