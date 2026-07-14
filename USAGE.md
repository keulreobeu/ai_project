# gstack Skills 사용법

이 문서는 VS Code GitHub Copilot에서 gstack 스타일 스킬을 사용하는 방법을 정리한다.

## 개요

이 프로젝트는 gstack 원본을 직접 실행하는 방식이 아니다.

대신 gstack의 `SKILL.md` 문서를 프로젝트 안에 넣어두고, Copilot에게 필요할 때 해당 문서를 참고하라고 지시하는 방식이다.

즉, 구조는 다음과 같다.

```text
gstack 원본 repo
→ 필요한 skill 폴더만 복사
→ 프로젝트의 .agents/skills/ 안에 배치
→ Copilot이 SKILL.md를 읽고 작업 방식에 반영
```

## 폴더 구조

권장 구조는 다음과 같다.

```text
ai_project/
├─ .agents/
│  └─ skills/
│     ├─ spec/
│     │  └─ SKILL.md
│     ├─ autoplan/
│     │  └─ SKILL.md
│     ├─ plan-eng-review/
│     │  └─ SKILL.md
│     ├─ investigate/
│     │  └─ SKILL.md
│     ├─ review/
│     │  └─ SKILL.md
│     ├─ qa/
│     │  └─ SKILL.md
│     ├─ docs/
│     │  └─ SKILL.md
│     └─ careful/
│        └─ SKILL.md
├─ .github/
│  └─ copilot-instructions.md
├─ AGENTS.md
├─ USAGE.md
└─ README.md
```

## gstack 원본 위치

gstack 원본은 작업 repo 안에 넣지 않는다.

권장 위치:

```text
/c/vscode/tools/gstack
```

작업 repo 위치:

```text
/c/vscode/ai_project
```

즉, 아래처럼 분리한다.

```text
/c/vscode/
├─ ai_project/      # 내 작업 repo
└─ tools/
   └─ gstack/       # gstack 원본 보관용
```

## gstack 원본 받기

```bash
cd /c/vscode
mkdir -p tools
cd tools
git clone https://github.com/garrytan/gstack.git
```

## 필요한 스킬 복사하기

작업 repo로 이동한다.

```bash
cd /c/vscode/ai_project
mkdir -p .agents/skills
```

기본 추천 스킬을 복사한다.

```bash
cp -r /c/vscode/tools/gstack/spec .agents/skills/
cp -r /c/vscode/tools/gstack/autoplan .agents/skills/
cp -r /c/vscode/tools/gstack/plan-eng-review .agents/skills/
cp -r /c/vscode/tools/gstack/investigate .agents/skills/
cp -r /c/vscode/tools/gstack/review .agents/skills/
cp -r /c/vscode/tools/gstack/qa .agents/skills/
cp -r /c/vscode/tools/gstack/docs .agents/skills/
cp -r /c/vscode/tools/gstack/careful .agents/skills/
```

복사 확인:

```bash
ls .agents/skills
```

정상 예시:

```text
autoplan  careful  docs  investigate  plan-eng-review  qa  review  spec
```

각 스킬의 `SKILL.md` 존재 여부 확인:

```bash
find .agents/skills -name "SKILL.md"
```

## 추천 스킬 설명

| Skill             | 용도                       |
| ----------------- | ------------------------ |
| `spec`            | 기능 요구사항을 구현 가능한 명세로 정리   |
| `autoplan`        | 작업 순서와 구현 계획 작성          |
| `plan-eng-review` | 구현 계획의 위험성, 순서, 누락 요소 검토 |
| `investigate`     | 에러 원인 분석, 디버깅            |
| `review`          | 코드 리뷰                    |
| `qa`              | 테스트 케이스, 검증 기준 정리        |
| `docs`            | README, 주석, 문서 작성        |
| `careful`         | 실수 방지, 변경 전 점검           |

## Copilot에서 사용하는 방법

VS Code에서 Copilot Chat 또는 Copilot Agent를 열고, 다음처럼 요청한다.

### 구현 계획 작성

```text
.agents/skills/autoplan/SKILL.md를 참고해서 이 기능 구현 계획을 짜줘.
```

예시:

```text
.agents/skills/autoplan/SKILL.md를 참고해서 로그인 기능 구현 계획을 짜줘.
```

### 요구사항 명세 작성

```text
.agents/skills/spec/SKILL.md를 참고해서 이 요구사항을 구현 가능한 명세로 바꿔줘.
```

예시:

```text
.agents/skills/spec/SKILL.md를 참고해서 게시판 CRUD 요구사항을 명세로 정리해줘.
```

### 구현 계획 검토

```text
.agents/skills/plan-eng-review/SKILL.md 기준으로 이 구현 계획의 위험성과 누락된 부분을 검토해줘.
```

### 에러 분석

```text
.agents/skills/investigate/SKILL.md를 참고해서 이 에러 원인을 분석해줘.
```

### 코드 리뷰

```text
.agents/skills/review/SKILL.md 기준으로 이 코드 리뷰해줘.
```

### 테스트 케이스 작성

```text
.agents/skills/qa/SKILL.md 기준으로 테스트 케이스를 정리해줘.
```

### 문서 작성

```text
.agents/skills/docs/SKILL.md를 참고해서 README를 작성해줘.
```

### 변경 전 점검

```text
.agents/skills/careful/SKILL.md 기준으로 이 변경이 위험한 부분이 있는지 점검해줘.
```

## slash command처럼 사용하기

아래 표현은 실제 명령어가 아니라 Copilot에게 작업 방식을 알려주는 약속이다.

```text
/spec
/autoplan
/review
/qa
/debug
/docs
```

예시:

```text
/autoplan 게시판 CRUD 구현 계획 짜줘
```

위 요청은 다음 의미로 사용한다.

```text
.agents/skills/autoplan/SKILL.md를 참고해서 게시판 CRUD 구현 계획을 작성한다.
```

더 안정적으로 사용하려면 파일 경로를 직접 적는 것이 좋다.

```text
.agents/skills/autoplan/SKILL.md를 참고해서 게시판 CRUD 구현 계획을 작성해줘.
```

## Git에 올릴 파일

작업 repo에는 아래 파일을 올린다.

```text
.agents/
.github/copilot-instructions.md
AGENTS.md
USAGE.md
```

커밋 명령어:

```bash
git add .agents .github AGENTS.md USAGE.md
git commit -m "Add Copilot agent skill guide"
git push
```

## Git에 올리지 않을 것

아래 항목은 보통 올리지 않는다.

```text
gstack 원본 폴더 전체
.env
API 키
토큰
비밀번호
가상환경 폴더
__pycache__
```

gstack 원본 폴더는 `/c/vscode/tools/gstack`에 보관하고, 작업 repo에는 필요한 스킬만 복사한다.

## 주의사항

Copilot이 항상 모든 파일을 자동으로 읽는 것은 아니다.

따라서 중요한 작업에서는 다음처럼 명확히 말하는 것이 좋다.

```text
먼저 AGENTS.md와 .agents/skills/autoplan/SKILL.md를 읽고 답변해줘.
```

또는:

```text
이 프로젝트의 AGENTS.md 규칙을 따르고, spec 스킬을 참고해서 답변해줘.
```

## 추천 작업 흐름

기능을 만들 때는 다음 순서로 사용한다.

```text
1. spec으로 요구사항 정리
2. autoplan으로 구현 계획 작성
3. plan-eng-review로 계획 검토
4. 구현
5. review로 코드 리뷰
6. qa로 테스트 케이스 작성
7. docs로 문서 정리
```

예시 흐름:

```text
1. .agents/skills/spec/SKILL.md를 참고해서 로그인 기능 명세를 작성해줘.
2. .agents/skills/autoplan/SKILL.md를 참고해서 구현 계획을 짜줘.
3. .agents/skills/plan-eng-review/SKILL.md 기준으로 계획을 검토해줘.
4. 구현해줘.
5. .agents/skills/review/SKILL.md 기준으로 코드 리뷰해줘.
6. .agents/skills/qa/SKILL.md 기준으로 테스트 케이스를 정리해줘.
```
