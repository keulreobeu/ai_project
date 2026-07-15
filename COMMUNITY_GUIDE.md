# 익명 커뮤니티 게시판 - 사용 가이드

## 개요

서울 축제 탐색 서비스에 익명 커뮤니티 게시판 기능이 추가되었습니다. 

### 특징

- ✅ **회원가입 불필요**: 익명으로 누구나 게시글 작성 가능
- ✅ **비밀번호 기반 권한**: 작성 시 비밀번호 등록, 수정/삭제 시에만 확인
- ✅ **SQLite 데이터베이스**: 파일 기반으로 별도 DB 서버 없음
- ✅ **4개 카테고리**: 자유게시판, 축제, 음식점, 팁 & 정보
- ✅ **기본 CRUD**: 목록 조회, 상세 조회, 작성, 수정, 삭제

## 기술 스택

- **프론트엔드**: Vue.js 3 (Composition API)
- **백엔드**: FastAPI + Python 비동기 처리
- **데이터베이스**: SQLite
- **스타일**: STYLE_GUIDE.md 기반 디자인

## 프로젝트 구조

```
backend/app/
├── models.py          # CommunityPost ORM 모델
├── schemas.py         # Pydantic 스키마
├── services.py        # 커뮤니티 비즈니스 로직
├── main.py            # 커뮤니티 API 라우터
└── ...

frontend/src/
├── pages/
│   └── CommunityPage.vue          # 게시판 메인 페이지
├── components/
│   ├── CommunityPostCard.vue       # 게시글 카드 (목록)
│   ├── CommunityPostForm.vue       # 게시글 작성 폼
│   ├── CommunityPostDetail.vue     # 게시글 상세 보기
│   └── CommunityPostEditForm.vue   # 게시글 수정 폼
└── ...
```

## 실행 방법

### 1. 백엔드 실행

```bash
cd backend
python run_server.py
```

- 자동으로 SQLite 테이블 생성
- API 서버 시작: http://127.0.0.1:8001
- FastAPI Docs: http://127.0.0.1:8001/docs

### 2. 프론트엔드 실행 (다른 터미널)

```bash
cd frontend
npm install
python run_frontend.py
```

- 개발 서버 시작: http://127.0.0.1:5173
- 자동으로 브라우저 열기

### 3. 접속

1. http://127.0.0.1:5173 열기
2. 상단 네비게이션에서 "커뮤니티" 클릭
3. 게시판 사용 시작

## API 엔드포인트

### 게시글 작성
```
POST /api/community/posts
Content-Type: application/json

{
  "category": "general",
  "title": "제목",
  "content": "내용",
  "password": "1234"
}
```

### 게시글 목록 조회
```
GET /api/community/posts?category=general
```

### 게시글 상세 조회
```
GET /api/community/posts/{post_id}
```

### 게시글 수정
```
PUT /api/community/posts/{post_id}
Content-Type: application/json

{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "password": "1234"
}
```

### 게시글 삭제
```
DELETE /api/community/posts/{post_id}?password=1234
```

## 주요 기능

### 1. 게시글 작성
- 카테고리 선택 (자유게시판, 축제, 음식점, 팁 & 정보)
- 제목 입력 (최대 100자)
- 내용 입력 (최대 5000자)
- 수정용 비밀번호 등록
- 실시간 글자 수 표시

### 2. 게시글 목록 조회
- 카테고리별 필터링
- 검색 기능 (제목 검색)
- 최신순 정렬
- 조회수 표시
- 작성 시간 표시

### 3. 게시글 상세 조회
- 전체 내용 표시
- 조회수 자동 증가
- 작성/수정 시간 표시
- 수정·삭제 버튼

### 4. 게시글 수정
- 비밀번호 확인 후 수정 가능
- 제목, 내용만 수정 (카테고리 변경 불가)
- 수정 시간 자동 업데이트

### 5. 게시글 삭제
- 비밀번호 확인 후 삭제 가능
- 삭제 확인 다이얼로그

## 데이터베이스 스키마

### community_posts 테이블
```sql
CREATE TABLE community_posts (
  post_id INTEGER PRIMARY KEY AUTOINCREMENT,
  category VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  content TEXT NOT NULL,
  password VARCHAR NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  view_count INTEGER DEFAULT 0
);
```

## 보안 고지

⚠️ **주의**: 이 구현은 **교육 목적**이며, 다음과 같은 특징이 있습니다:

1. **비밀번호는 평문 저장**: 암호화 없이 저장됨
2. **사용자 인증 없음**: 익명으로 누구나 작성 가능
3. **권한 검사 없음**: 비밀번호 일치만으로 수정/삭제 허가

프로덕션 환경에서는:
- bcrypt 등으로 비밀번호 해싱 필수
- 사용자 인증/인가 체계 구현
- HTTPS 사용
- CSRF 보호
- 입력값 검증 강화

## 테스트

### 게시글 작성 테스트
1. "새 글쓰기" 버튼 클릭
2. 제목, 내용, 비밀번호 입력
3. "작성하기" 클릭
4. 목록에 새 글이 추가되는지 확인

### 게시글 수정 테스트
1. 게시글 클릭하여 상세 보기
2. "⋯" 메뉴에서 "수정" 클릭
3. 내용 수정 및 비밀번호 입력
4. "수정하기" 클릭
5. "수정" 시간이 업데이트되는지 확인

### 게시글 삭제 테스트
1. 게시글 클릭하여 상세 보기
2. "⋯" 메뉴에서 "삭제" 클릭
3. 비밀번호 입력
4. "삭제" 확인
5. 목록에서 게시글이 제거되는지 확인

### 비밀번호 오류 테스트
1. 게시글 수정/삭제 시 잘못된 비밀번호 입력
2. "잘못된 비밀번호" 오류 메시지 확인

## 문제 해결

### API 연결 실패
```
Failed to load posts: Failed to fetch
```
- 백엔드 서버가 실행 중인지 확인
- http://127.0.0.1:8001/api/health 접속 테스트
- 포트 충돌 확인 (기본값: 8001)

### 데이터베이스 오류
```
sqlite3.OperationalError: no such table
```
- 백엔드 서버 재시작 (테이블 자동 생성)
- `project/seoul_festival.db` 파일 삭제 후 재시작

### 게시글이 저장되지 않음
- 브라우저 콘솔에서 네트워크 오류 확인
- 입력값이 모두 채워졌는지 확인
- 비밀번호 최소 1글자 확인

## 향후 개선 사항

- [ ] 페이지네이션 추가
- [ ] 댓글 기능 추가
- [ ] 이미지 첨부 기능
- [ ] 신고 기능
- [ ] 자동 저장 (드래프트)
- [ ] 마크다운 지원
- [ ] 고급 검색 필터
- [ ] 최근 검색어 저장

## 라이선스 및 저작권

본 익명 게시판은 교육 목적으로 제작되었습니다.
기존 데이터(축제, 관광지 등)는 공공 데이터를 사용하며, 각 데이터의 라이선스를 준수합니다.
