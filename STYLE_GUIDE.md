# 서울 축제 안내 웹서비스 UI 스타일 가이드

## 1. 디자인 컨셉

본 웹서비스는 서울의 축제와 관광 정보를 쉽고 빠르게 탐색할 수 있는 관광 포털형 웹사이트를 지향한다.
전체 분위기는 밝고 깔끔하며, 축제 이미지와 지도 정보를 중심으로 구성한다.

### 핵심 키워드

```text
서울
축제
관광
지도
추천
큐레이션
밝음
깔끔함
모바일 친화
```

### 디자인 방향

```text
큰 이미지 중심의 메인 화면
카드형 축제 갤러리
지도와 축제 정보가 결합된 상세 화면
우측 하단 고정 챗봇 버튼
간결한 익명 게시판 UI
```

---

## 2. 컬러 스타일

### 기본 색상

```css
--color-primary: #00AEEF;   /* 메인 포인트 블루 */
--color-secondary: #FF6B35; /* 축제 강조 오렌지 */
--color-accent: #7AC943;    /* 자연·야외 행사 느낌 */
--color-bg: #F8FAFC;        /* 전체 배경 */
--color-card: #FFFFFF;      /* 카드 배경 */
--color-text: #222222;      /* 기본 텍스트 */
--color-muted: #6B7280;     /* 보조 텍스트 */
--color-border: #E5E7EB;    /* 경계선 */
--color-danger: #EF4444;    /* 삭제·오류 */
```

### 색상 사용 기준

| 용도     | 색상        | 사용 위치                |
| ------ | --------- | -------------------- |
| 메인 색상  | `#00AEEF` | 주요 버튼, 링크, 활성 메뉴     |
| 보조 색상  | `#FF6B35` | 축제 태그, 지도 핀, 강조 배지   |
| 액센트 색상 | `#7AC943` | 추천 표시, 자연·야외 축제      |
| 배경 색상  | `#F8FAFC` | 전체 페이지 배경            |
| 카드 색상  | `#FFFFFF` | 축제 카드, 정보 패널, 게시글 카드 |
| 위험 색상  | `#EF4444` | 삭제 버튼, 오류 메시지        |

---

## 3. 폰트 스타일

### 기본 폰트

```css
font-family: "Pretendard", "Noto Sans KR", sans-serif;
```

### 폰트 크기 기준

| 요소    |          크기 |  굵기 |
| ----- | ----------: | --: |
| 메인 제목 | 42px ~ 56px | 700 |
| 섹션 제목 | 28px ~ 36px | 700 |
| 카드 제목 | 20px ~ 24px | 700 |
| 본문    |        16px | 400 |
| 보조 설명 | 13px ~ 14px | 400 |
| 버튼    | 15px ~ 16px | 600 |

### 텍스트 스타일 방향

```text
제목은 짧고 굵게 작성한다.
본문은 2~3줄 이내로 간결하게 구성한다.
날짜, 장소, 조회수 등 보조 정보는 회색 계열로 표시한다.
```

---

## 4. 전체 레이아웃 스타일

### 기본 컨테이너

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

### 섹션 간격

```css
.section {
  padding: 80px 0;
}
```

### 레이아웃 특징

```text
넓은 여백을 사용해 관광 포털 느낌을 준다.
이미지와 카드 사이 간격을 충분히 둔다.
정보가 많아도 복잡해 보이지 않도록 섹션을 명확히 나눈다.
```

---

## 5. 헤더 스타일

### 구성

```text
로고 | 축제보기 | 지도보기 | 게시판 | 챗봇 | 검색
```

### 스타일

```css
.header {
  height: 72px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #E5E7EB;
  position: sticky;
  top: 0;
  z-index: 100;
}
```

### 디자인 기준

```text
스크롤해도 상단에 고정한다.
흰색 또는 반투명 흰색 배경을 사용한다.
현재 선택된 메뉴는 메인 컬러로 강조한다.
메뉴 hover 시 밑줄 또는 색상 변경 효과를 준다.
```

---

## 6. 메인 히어로 영역 스타일

### 구성

```text
큰 축제 이미지
축제명
축제 기간
장소
상세보기 버튼
지도에서 보기 버튼
```

### 스타일

```css
.hero {
  height: 520px;
  border-radius: 0 0 40px 40px;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
}

.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.55)
  );
}
```

### 디자인 기준

```text
이미지는 화면에서 가장 먼저 보이는 핵심 요소로 사용한다.
텍스트가 잘 보이도록 이미지 위에 어두운 그라데이션을 적용한다.
버튼은 둥근 pill 형태로 구성한다.
```

---

## 7. 축제 갤러리 카드 스타일

### 카드 구성

```text
대표 이미지
카테고리 태그
축제명
기간
장소
상세보기 버튼
```

### 카드 스타일

```css
.festival-card {
  background: #FFFFFF;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.festival-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.14);
}
```

### 이미지 스타일

```css
.festival-card img {
  width: 100%;
  height: 220px;
  object-fit: cover;
}
```

### 갤러리 레이아웃

```css
.festival-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}
```

### 디자인 기준

```text
축제 이미지를 카드의 중심 요소로 둔다.
hover 시 살짝 떠오르는 효과를 준다.
카드 모서리는 둥글게 처리한다.
카드 내부 정보는 날짜, 장소, 제목 순으로 가독성 있게 배치한다.
```

---

## 8. 지도 및 상세 정보 화면 스타일

### 기본 구조

```text
왼쪽: 지도
오른쪽: 축제 상세 정보 패널
```

### 레이아웃

```css
.detail-layout {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 32px;
}
```

### 지도 영역

```css
.map-box {
  height: 560px;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid #E5E7EB;
}
```

### 상세 정보 패널

```css
.info-panel {
  background: #FFFFFF;
  border-radius: 28px;
  padding: 32px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}
```

### 지도 핀 스타일

```css
.map-pin {
  width: 44px;
  height: 44px;
  background: #FF6B35;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.35);
}
```

### 디자인 기준

```text
지도는 넓고 시원하게 보여준다.
상세 정보 패널은 카드처럼 분리한다.
지도 핀은 오렌지 계열로 강조한다.
축제명, 날짜, 장소는 상단에 명확히 배치한다.
```

---

## 9. 챗봇 플로팅 버튼 스타일

### 위치

```text
모든 화면의 우측 하단에 고정한다.
```

### 스타일

```css
.chatbot-floating {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00AEEF, #7AC943);
  box-shadow: 0 12px 30px rgba(0, 174, 239, 0.35);
  z-index: 999;
}
```

### 디자인 기준

```text
항상 눈에 띄지만 콘텐츠를 가리지 않게 배치한다.
말풍선 아이콘 또는 관광 안내 캐릭터 아이콘을 사용한다.
hover 시 크기가 살짝 커지는 효과를 줄 수 있다.
```

---

## 10. 챗봇 채팅 화면 스타일

### 화면 구성

```text
상단: 챗봇 이름, 뒤로가기 버튼
중앙: 대화 메시지 목록
하단: 입력창, 전송 버튼
```

### 전체 레이아웃

```css
.chat-page {
  max-width: 760px;
  margin: 0 auto;
  height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
}
```

### 챗봇 메시지

```css
.chat-message.bot {
  align-self: flex-start;
  background: #F1F5F9;
  border-radius: 20px 20px 20px 4px;
}
```

### 사용자 메시지

```css
.chat-message.user {
  align-self: flex-end;
  background: #00AEEF;
  color: #FFFFFF;
  border-radius: 20px 20px 4px 20px;
}
```

### 디자인 기준

```text
챗봇 메시지와 사용자 메시지를 색상과 정렬로 구분한다.
입력창은 화면 하단에 고정한다.
추천 질문 버튼은 둥근 칩 형태로 제공한다.
```

---

## 11. 게시판 스타일

### 게시판 목록 스타일

```text
제목
익명이름
작성일
조회수
내용 미리보기
```

### 게시글 카드 스타일

```css
.board-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 20px;
  padding: 24px;
  transition: box-shadow 0.2s ease;
}

.board-card:hover {
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}
```

### 작성 폼 스타일

```css
.board-form input,
.board-form textarea {
  width: 100%;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  padding: 14px 16px;
  font-size: 16px;
}

.board-form textarea {
  min-height: 180px;
  resize: vertical;
}
```

### 글자수 표시

```css
.char-count {
  text-align: right;
  font-size: 13px;
  color: #6B7280;
}
```

### 디자인 기준

```text
게시판은 관광 사이트 분위기에 맞게 딱딱한 표보다는 카드형 목록을 우선 사용한다.
작성 폼은 입력 영역을 넓게 구성한다.
수정, 삭제 버튼은 일반 버튼과 명확히 구분한다.
삭제 버튼은 위험 색상으로 표시한다.
```

---

## 12. 버튼 스타일

### 기본 버튼

```css
.btn-primary {
  background: #00AEEF;
  color: #FFFFFF;
  border-radius: 999px;
  padding: 12px 22px;
  font-weight: 700;
}
```

### 보조 버튼

```css
.btn-outline {
  background: #FFFFFF;
  color: #00AEEF;
  border: 1px solid #00AEEF;
  border-radius: 999px;
  padding: 12px 22px;
}
```

### 삭제 버튼

```css
.btn-danger {
  background: #EF4444;
  color: #FFFFFF;
  border-radius: 999px;
  padding: 12px 22px;
  font-weight: 700;
}
```

### 디자인 기준

```text
주요 행동은 파란색 버튼으로 표시한다.
보조 행동은 테두리 버튼으로 표시한다.
삭제처럼 위험한 행동은 빨간색 버튼으로 구분한다.
```

---

## 13. 태그 스타일

### 태그 예시

```text
#무료
#야간축제
#가족추천
#전시
#공연
#한강
#이번주
```

### 기본 태그 스타일

```css
.tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: #E0F2FE;
  color: #0369A1;
  font-size: 13px;
  font-weight: 600;
}
```

### 카테고리별 색상 예시

| 카테고리 | 색상 방향 |
| ---- | ----- |
| 음악   | 보라    |
| 전시   | 파랑    |
| 야시장  | 오렌지   |
| 전통   | 초록    |
| 가족   | 노랑    |
| 무료   | 민트    |

---

## 14. 검색 및 필터 스타일

### 필터 항목

```text
지역
날짜
카테고리
무료/유료
실내/야외
진행중/예정
```

### 검색바 스타일

```css
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 999px;
  padding: 12px 20px;
}
```

### 디자인 기준

```text
검색창은 둥근 형태로 구성한다.
필터는 칩 또는 드롭다운 형태로 제공한다.
선택된 필터는 메인 컬러로 강조한다.
```

---

## 15. 모달 스타일

### 사용 위치

```text
게시글 수정 비밀번호 확인
게시글 삭제 비밀번호 확인
오류 또는 확인 메시지
```

### 스타일

```css
.modal {
  background: #FFFFFF;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.25);
}

.modal-backdrop {
  background: rgba(15, 23, 42, 0.45);
}
```

### 디자인 기준

```text
배경은 어둡게 처리해 모달에 집중하게 한다.
확인 버튼과 취소 버튼을 명확히 구분한다.
삭제 확인 모달은 위험 색상을 사용한다.
```

---

## 16. 반응형 스타일

### PC

```text
헤더 전체 메뉴 노출
히어로 이미지 크게 표시
축제 카드 3열
지도와 정보 패널 2단 배치
```

### 태블릿

```text
축제 카드 2열
지도와 정보 패널 간격 축소
헤더 메뉴 간격 축소
```

### 모바일

```text
햄버거 메뉴 사용
축제 카드 1열
지도 먼저, 상세 정보 아래 배치
챗봇 버튼 크기 축소
게시판 목록은 카드형으로 단순화
```

### 모바일 기준 스타일

```css
@media (max-width: 768px) {
  .hero {
    height: 360px;
    border-radius: 0 0 28px 28px;
  }

  .festival-grid {
    grid-template-columns: 1fr;
  }

  .detail-layout {
    grid-template-columns: 1fr;
  }

  .chatbot-floating {
    width: 56px;
    height: 56px;
    right: 20px;
    bottom: 20px;
  }
}
```

---

## 17. 전체 스타일 요약

```text
전체 분위기:
밝고 깔끔한 서울 관광 포털형 UI

핵심 요소:
큰 축제 이미지
카드형 갤러리
지도 기반 상세 화면
우측 하단 챗봇 버튼
카드형 익명 게시판

주요 색상:
블루, 오렌지, 화이트, 연한 회색

스타일 특징:
둥근 모서리
넓은 여백
부드러운 그림자
이미지 중심 레이아웃
모바일 친화 구조
```
