# AGENTS.md

이 저장소는 VS Code GitHub Copilot Agent에서 gstack 스타일의 작업 흐름을 참고하기 위해 구성되었다.

Copilot은 이 문서와 `.agents/skills/` 내부의 `SKILL.md` 파일들을 참고하여 작업한다.

## 목적

이 프로젝트의 AI Agent는 단순히 코드를 바로 작성하는 것이 아니라, 작업 유형에 따라 적절한 스킬을 선택하고 다음 흐름으로 진행한다.

1. 요청 의도 파악
2. 관련 스킬 선택
3. 작업 계획 수립
4. 최소 단위로 구현
5. 검증 방법 제안
6. 변경 내용 요약

## Skill 위치

스킬 문서는 아래 위치에 있다.

```text
.agents/skills/
```

각 스킬은 다음과 같은 구조를 가진다.

```text
.agents/skills/{skill-name}/SKILL.md
```

예시:

```text
.agents/skills/spec/SKILL.md
.agents/skills/autoplan/SKILL.md
.agents/skills/plan-eng-review/SKILL.md
.agents/skills/investigate/SKILL.md
.agents/skills/review/SKILL.md
.agents/skills/qa/SKILL.md
.agents/skills/docs/SKILL.md
.agents/skills/careful/SKILL.md
```

## 기본 사용 규칙

Copilot은 사용자의 요청을 보고 가장 적절한 스킬을 선택해야 한다.

사용자가 특정 스킬을 직접 언급한 경우, 해당 스킬을 우선 참고한다.

예시:

```text
.agents/skills/spec/SKILL.md를 참고해서 명세 작성해줘.
```

```text
gstack의 autoplan 방식으로 구현 계획을 짜줘.
```

```text
review 스킬 기준으로 코드 리뷰해줘.
```

## 주요 스킬

| Skill             | 용도                     |
| ----------------- | ---------------------- |
| `spec`            | 기능 요구사항을 구현 가능한 명세로 정리 |
| `autoplan`        | 전체 작업 계획 작성            |
| `plan-eng-review` | 개발/구현 관점에서 계획 검토       |
| `investigate`     | 버그 원인 분석 및 디버깅         |
| `review`          | 코드 리뷰                  |
| `qa`              | 테스트 및 검증 관점 점검         |
| `docs`            | 문서화                    |
| `careful`         | 실수 방지, 변경 전 위험 점검      |

## 작업 방식

Copilot은 작업 전에 다음 내용을 짧게 정리한다.

```text
- 어떤 작업인지
- 어떤 스킬을 참고할지
- 변경 범위가 어디까지인지
- 위험하거나 확인이 필요한 부분이 있는지
```

단순 질문에는 긴 계획 없이 바로 답변해도 된다.

## 코드 변경 원칙

코드를 수정할 때는 다음 원칙을 따른다.

1. 한 번에 너무 많은 파일을 바꾸지 않는다.
2. 변경 이유를 명확히 설명한다.
3. 기존 동작을 깨뜨릴 가능성이 있으면 먼저 언급한다.
4. 테스트 가능한 경우 테스트 방법을 같이 제안한다.
5. 불확실한 요구사항은 임의로 확장하지 않는다.
6. 보안 정보, API 키, 비밀번호, 토큰은 코드에 포함하지 않는다.

## 명령어처럼 보이는 표현 처리

`/spec`, `/debug`, `/review`, `/qa`, `/docs`, `/autoplan` 같은 표현은 실제 터미널 명령어가 아니다.

이 표현들은 `.agents/skills/` 안의 해당 스킬 문서를 참고하라는 의미로 해석한다.

예시:

```text
/spec 로그인 기능 정리해줘
```

위 요청은 다음 의미로 처리한다.

```text
.agents/skills/spec/SKILL.md를 참고해서 로그인 기능을 구현 가능한 명세로 정리한다.
```

## 기본 응답 형식

가능하면 다음 순서로 답변한다.

```text
1. 이해한 내용
2. 적용할 스킬
3. 작업 계획
4. 구현 또는 분석 결과
5. 검증 방법
6. 다음 작업 제안
```

단, 사용자가 짧은 답변을 원하거나 단순 질문을 한 경우에는 간단히 답변한다.

## 금지 사항

* 스킬 문서를 실제 실행 가능한 프로그램처럼 취급하지 않는다.
* slash command를 터미널 명령어로 실행하지 않는다.
* 사용자가 요청하지 않은 대규모 리팩토링을 하지 않는다.
* 민감한 정보를 저장소에 커밋하지 않는다.
* `.env`, 토큰, 비밀번호, 인증 키를 노출하지 않는다.

## 권장 사용 예시

```text
.agents/skills/autoplan/SKILL.md를 참고해서 게시판 CRUD 구현 계획을 짜줘.
```

```text
.agents/skills/spec/SKILL.md를 참고해서 이 요구사항을 명세로 바꿔줘.
```

```text
.agents/skills/investigate/SKILL.md를 참고해서 이 에러 원인을 분석해줘.
```

```text
.agents/skills/review/SKILL.md 기준으로 이 코드 리뷰해줘.
```

```text
.agents/skills/qa/SKILL.md 기준으로 테스트 케이스를 정리해줘.
```
