"""Seed realistic community posts for each board category."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone

from app.models import CommunityPost
from app.orm import SessionLocal


KST = timezone(timedelta(hours=9))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2_sha256$100000${salt.hex()}${derived_key.hex()}"


POSTS = {
    "general": [
        ("서울 축제 다닐 때 대중교통이 제일 편하네요", "지난 주말에 종로 쪽 행사 두 곳을 연달아 다녀왔는데 주차 걱정 없이 지하철로 움직이니 훨씬 편했습니다. 행사장 근처 역의 출구 번호를 미리 확인해 두면 덜 헤매는 것 같아요."),
        ("비 오는 날에도 갈 만한 실내 행사가 있을까요?", "주말에 비 예보가 있어서 야외 축제 대신 실내에서 볼 수 있는 전시나 행사를 찾고 있습니다. 직접 다녀온 곳 중에 대중교통으로 가기 편한 곳이 있으면 알려주세요."),
        ("축제 사진 찍을 때 챙기면 좋은 준비물", "해가 지고 나면 생각보다 기온이 많이 내려가서 얇은 겉옷이 꼭 필요했습니다. 휴대용 배터리랑 작은 우산도 챙기니 하루 종일 돌아다니기 좋았어요."),
        ("이번 달 가족과 함께 갈 곳을 찾고 있어요", "초등학생 조카와 부모님이 같이 즐길 수 있는 행사를 알아보는 중입니다. 체험 프로그램이 있고 오래 걷지 않아도 되는 곳이면 좋겠습니다."),
        ("행사 종료 시간보다 조금 일찍 가는 걸 추천해요", "종료 직전에 방문했더니 일부 체험 부스가 먼저 마감되어 아쉬웠습니다. 인기 프로그램이 있는 행사는 최소 두세 시간 전에 도착하는 게 안전해 보여요."),
    ],
    "festival": [
        ("문학주간 다녀오신 분 동선 추천 부탁드려요", "북토크와 전시를 같은 날 보고 싶은데 프로그램 사이 이동 시간이 어느 정도인지 궁금합니다. 마로니에공원 주변에서 잠깐 쉬기 좋은 곳도 함께 추천해 주세요."),
        ("서울국제작가축제 사전 신청 확인하세요", "관심 있던 대담 프로그램이 조기 마감될 수 있다고 해서 미리 신청했습니다. 현장 방문 전에 공식 홈페이지에서 프로그램별 신청 여부를 확인하는 게 좋겠습니다."),
        ("수국축제는 오전 방문이 여유로웠어요", "사람이 몰리기 전 오전 시간에 도착하니 사진도 편하게 찍고 산책로도 천천히 둘러볼 수 있었습니다. 햇빛이 강해서 모자와 물은 꼭 챙기는 걸 추천합니다."),
        ("덕수궁 야간 행사 예약 성공했어요", "예약 시간보다 조금 일찍 도착해서 주변을 둘러보니 좋았습니다. 야간에는 돌길이 어두운 구간이 있어서 편한 신발을 신고 가는 편이 좋겠어요."),
        ("게임 e스포츠 서울 관람 계획 공유합니다", "오전에는 전시와 체험존을 보고 오후에 주요 경기를 관람할 예정입니다. DDP 주변이 주말에 붐비는 편이라 식사는 조금 이른 시간에 하려고 합니다."),
    ],
    "restaurant": [
        ("DDP 행사 보고 근처에서 늦은 점심 먹었어요", "행사장 바로 앞은 대기 줄이 길어서 골목 안쪽으로 조금 이동했습니다. 오후 두 시가 지나니 자리가 여유로워졌고 여러 명이 앉을 수 있는 식당도 찾기 쉬웠어요."),
        ("대학로 공연 전 식사는 여유 있게 잡으세요", "주말 저녁에는 인기 식당 대기가 길어서 공연 시작 한 시간 반 전에는 도착하는 게 좋았습니다. 간단히 먹으려면 혜화역 반대편 골목도 선택지가 많아요."),
        ("서울광장 행사 때 이용하기 좋은 식사 동선", "시청역 주변은 점심시간에 직장인 손님이 많았습니다. 행사 관람 후 덕수궁 돌담길 방향으로 이동하면 카페와 식당을 함께 찾기 편했습니다."),
        ("양재 행사장 근처 식당은 미리 확인하세요", "aT센터 안에서 행사가 열리는 날에는 주변 식당도 금방 붐볐습니다. 양재시민의숲역 근처까지 범위를 넓히면 비교적 선택지가 많았습니다."),
        ("축제장에서 음식 살 때 작은 가방이 편해요", "푸드트럭 음식을 들고 이동할 일이 많아 양손을 쓸 수 있는 작은 크로스백이 유용했습니다. 쓰레기통 위치도 입장할 때 미리 봐두면 편합니다."),
    ],
    "tips": [
        ("주말 축제 같이 둘러볼 분 구해요", "토요일 오후에 종로 일대 축제와 전시를 천천히 둘러볼 예정입니다. 사진 촬영과 산책을 좋아하고 일정 조율이 가능한 분이면 댓글로 계획을 나눠주세요."),
        ("축제 사진 촬영 동행 찾습니다", "야간 조명과 공연 장면을 촬영해 보고 싶습니다. 전문 장비가 없어도 괜찮고 서로 사진을 공유하면서 안전하게 이동할 분을 찾고 있어요."),
        ("가족 체험 프로그램 정보 같이 모아봐요", "아이와 참여할 수 있는 무료 체험 행사 정보를 정리하고 있습니다. 연령 제한이나 사전 예약 여부를 확인한 분들이 댓글로 알려주시면 함께 업데이트하겠습니다."),
        ("서울 동쪽 지역 행사 정보 공유방 만들어요", "성동구, 광진구, 송파구 쪽에서 열리는 소규모 행사 정보를 놓치지 않으려고 합니다. 공식 링크와 방문 후기를 중심으로 편하게 공유하면 좋겠습니다."),
        ("외국인 친구와 갈 축제 추천 부탁드립니다", "한국어가 익숙하지 않은 친구와 함께 갈 예정이라 안내 표지나 영어 프로그램이 잘 준비된 행사를 찾고 있습니다. 직접 방문해 본 경험이 있다면 알려주세요."),
    ],
}


def seed_posts() -> int:
    db = SessionLocal()
    created = 0
    try:
        db.query(CommunityPost).filter(CommunityPost.category == "team").update(
            {CommunityPost.category: "tips"},
            synchronize_session=False,
        )
        base_time = datetime.now(KST) - timedelta(days=8)
        password_hash = hash_password("0000")
        sequence = 0
        for category, posts in POSTS.items():
            for title, content in posts:
                exists = db.query(CommunityPost).filter(
                    CommunityPost.category == category,
                    CommunityPost.title == title,
                ).first()
                if exists:
                    continue
                db.add(CommunityPost(
                    category=category,
                    title=title,
                    content=content,
                    password=password_hash,
                    created_at=base_time + timedelta(hours=sequence * 9),
                    view_count=12 + sequence * 7,
                ))
                sequence += 1
                created += 1
        db.commit()
        return created
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Created {seed_posts()} community posts.")
