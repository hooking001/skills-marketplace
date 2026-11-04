# Pretendard v1.3.9

정적 OTF 9종과 SIL Open Font License 1.1 원문을 함께 제공한다.
시스템 글꼴 설치 없이 모든 Typst 컴파일에 `--font-path fonts/Pretendard`를 전달한다.

생성한 프로젝트 루트에서 무결성 검사:

```bash
(cd fonts/Pretendard && shasum -a 256 -c SHA256SUMS)
```

재다운로드가 필요하면 `python3 /path/to/skill/assets/scripts/manual.py fonts`를 실행한다.
공식 배포: https://github.com/orioncactus/pretendard/releases/tag/v1.3.9
코드용 Menlo/Courier New는 시스템 글꼴이며 이 패키지에 포함되지 않는다.

번들 폰트는 스킬 루트의 `assets/project/fonts/Pretendard/`에 있으며, `fonts` 명령은 이 경로만 갱신한다. 이미 생성한 프로젝트의 폰트는 변경하지 않는다.

네트워크 없이 공식 ZIP을 사용할 때:

```bash
python3 /path/to/skill/assets/scripts/manual.py fonts --archive /path/to/Pretendard-1.3.9.zip
```

프로젝트 생성과 빌드는 번들 폰트를 사용하므로 재다운로드가 필요하지 않다.
