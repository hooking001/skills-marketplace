# Nangate45 / Liberty RTL Skill

Linux·macOS에서 RTL 시뮬레이션, Yosys 표준 셀 매핑, 면적·셀 통계 산출과 독립 프로젝트 생성을 지원합니다. Nangate45 typical이 기본이며 다른 Liberty도 선택할 수 있습니다. PnR, STA, 전력 분석은 제공하지 않습니다.

## 준비

- Python **3.8 이상**, Bash (macOS 기본 Bash 3.2 포함)
- 합성: ABC를 포함한 Yosys
- 시뮬레이션: Icarus Verilog (`iverilog`, `vvp`)
- 누락 라이브러리 다운로드: curl

도구는 PATH 또는 `YOSYS`, `IVERILOG`, `VVP`에 지정한 **실행 파일 경로**에서 찾습니다. 환경변수에 옵션을 함께 넣지 마세요. GNU 전용 sed/readlink/sha256sum, 고정 Homebrew 경로, 시스템 설정 변경을 요구하지 않습니다. Python은 macOS 기본 제공을 가정하지 않습니다.

Yosys와 Icarus는 Linux·macOS용 [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build)를 사용할 수 있습니다. 배포판 패키지를 사용하는 경우 해당 패키지에서 ABC도 제공하는지 확인하세요.

## 사용

이 문서의 명령은 스킬 루트에서 실행합니다. 경로에 공백이 있으면 인용하세요.

```bash
# 기본 Nangate45 프로젝트. 출력 경로가 이미 존재하면 실패합니다.
bash scripts/setup_project.sh counter /path/to/work

# 다른 공정·코너 및 프로젝트명과 다른 top을 선택합니다.
bash scripts/setup_project.sh counter /path/to/work --top counter_top --liberty /path/to/corner.lib

bash /path/to/work/counter/script/run_tb.sh
bash /path/to/work/counter/script/run_synth.sh
bash /path/to/work/counter/clean.sh

# 포함된 가산기: 512개 입력 검사와 합성
bash example/full_adder_4bit/run_all.sh
bash example/full_adder_4bit/clean.sh
```

프로젝트는 `rtl/`, `tb/`, `script/`, `lib/`, `synth/`, `dump/`, `project.json`으로 구성됩니다. 기본 RTL은 비동기 리셋을 갖는 4비트 증가기이며 생성 TB가 16개 입력과 리셋을 검사합니다. 생성 프로젝트에 라이브러리·실행기를 복사하므로 원본 스킬에 의존하지 않습니다. 포함 가산기 예제는 스킬 내부의 공통 실행기와 자산을 사용합니다.

`project.json`의 `top`, `tb_top`, `liberty`를 수정하고 `script/rtl.f`, `script/tb.f`에 소스 경로를 한 줄에 하나씩 지정합니다. 상대 소스 경로는 해당 파일리스트 기준, 상대 Liberty 경로는 프로젝트 루트 기준입니다. 파일리스트는 공백 경로, 선택적인 바깥 인용부호, CRLF, 빈 줄, 전체 줄 `#`/`//` 주석을 허용합니다. `+incdir`, `-D`, `-f`, glob, 인라인 주석은 지원하지 않습니다. `.sv`는 Yosys `read_verilog -sv`로 읽지만 완전한 SystemVerilog 지원을 보장하지 않습니다.

```bash
bash /path/to/work/counter/script/run_synth.sh other_top --liberty lib/other.lib
bash /path/to/work/counter/script/run_tb.sh other_top --tb-top other_top_tb
```

실행 디렉터리는 자유롭습니다. 시뮬레이션은 `script/`에서 실행되며 기본 TB는 `../dump/<top>.vcd`를 기록합니다. 실행기는 `.rtl-flow-outputs.json`에 기록된 파일만 정리합니다. 커스텀 TB의 다른 파형 경로는 직접 관리하세요.

## 라이브러리 검증과 결과 해석

```bash
bash scripts/download_nangate45.sh                   # 포함 파일 SHA-256 검증
bash scripts/download_nangate45.sh /path/to/new/lib  # 고정 커밋에서 다운로드·검증
```

해시가 다른 기존 파일은 덮어쓰지 않습니다. 다운로드 실패·해시 오류 시 임시 파일은 폐기합니다. 출처·커밋·원본 라이선스는 [resources/PROVENANCE.md](resources/PROVENANCE.md)에 있습니다.

넷리스트, 전체 로그와 최종 통계, 재현 명령은 `synth/`에 저장합니다. 미매핑 셀이나 연결 오류가 있으면 실패하며 이전 넷리스트가 성공 결과로 남지 않게 합니다. 면적은 선택한 Liberty의 셀 면적 합계이며 배치 면적·STA 결과·등가성 증명이 아닙니다. 셀 수와 NAND2 환산 게이트 수를 구분하세요. 정확한 수치는 도구 버전과 최적화에 따라 달라집니다.

## 설치

마켓플레이스에서는 `nangate45` 플러그인을 설치합니다. 독립 복사 설치가 필요하면 아래 명령을 사용합니다. 기존 설치 경로는 덮어쓰지 않으며 원하는 **하나의** 대상만 설치합니다.

```bash
bash install.sh                                  # ${CODEX_HOME:-~/.codex}/skills/nangate45
bash install.sh --target claude                   # ~/.claude/skills/nangate45
bash install.sh --target antigravity              # ~/.gemini/config/skills/nangate45
bash install.sh --destination /path/to/skills     # /path/to/skills/nangate45
```

스킬 이름을 `nangate45_skill`에서 `nangate45`로 정규화했습니다. 이전 설치가 있다면 새 설치를 확인한 뒤 중복 발견을 방지하도록 이전 폴더를 직접 정리하세요. 예전 `init_rtl_dir` 별칭을 자동 생성하지 않습니다.

## 검증

```bash
python3 -m unittest discover -s tests -v
```

생성·이동·덮어쓰기 거부·체크섬·설치·정리와 실패 전달을 로컬에서 검사합니다. EDA 도구가 있으면 가산기, 순차 RTL, 공백 경로, 테스트 실패와 합성 실패도 실제로 실행합니다. 도구가 없으면 해당 통합 검사만 skip합니다. GitHub CI는 사용하지 않습니다.
