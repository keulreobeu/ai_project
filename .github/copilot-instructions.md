# Copilot Project Instructions

이 프로젝트에서는 gstack 스타일의 AI engineering workflow를 참고한다.

## General behavior

- 답변하기 전에 현재 작업이 기획, 명세, 구현, 리뷰, 디버깅, QA, 릴리즈 중 어디에 해당하는지 판단한다.
- 가능한 경우 `.agents/skills/` 안의 관련 `SKILL.md` 지침을 우선 참고한다.
- 작업 전에는 변경 범위와 위험도를 짧게 정리한다.
- 구현 시에는 작은 단위로 변경하고, 변경 이유를 명확히 남긴다.
- 테스트 가능한 변경은 테스트 방법을 함께 제안한다.
- 불확실한 요구사항은 바로 구현하지 말고, 먼저 명세를 좁힌다.

## gstack skills

- 기획/아이디어 검증: `.agents/skills/office-hours/SKILL.md`
- 요구사항 명세화: `.agents/skills/spec/SKILL.md`
- 구현 계획: 관련 engineering 또는 planning skill
- 코드 리뷰: review 관련 skill
- 디버깅: debug 관련 skill
- 릴리즈/배포: release 관련 skill

## Invocation style

사용자가 다음과 같이 말하면 해당 skill을 참고한다.

- `/office-hours`: 제품/아이디어 검토
- `/spec`: 요구사항을 구현 가능한 명세로 변환
- `/debug`: 버그 원인 분석
- `/review`: 코드 리뷰
- `/qa`: 테스트 관점 점검
- `/release`: 릴리즈 준비 점검

Copilot은 위 명령어를 실제 CLI 명령으로 실행하지 말고, 해당 skill 문서의 역할과 체크리스트를 참고해서 답변한다.