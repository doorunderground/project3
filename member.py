# member.py
from db import fetch_one, execute

# 회원정보, 현재등급, 할인율
def get_member_info(member_id: int): 
    return fetch_one(
        """
        SELECT m.회원_id, m.회원명, m.가입일시,
               g.등급_id, g.등급이름, g.할인율, g.최소포인트
        FROM 회원 m
        LEFT JOIN 등급 g ON m.등급_id = g.등급_id
        WHERE m.회원_id=%s
        """,
        (member_id,),
    )


def get_member_points(member_id: int) -> int:
    row = fetch_one(
        "SELECT COALESCE(SUM(포인트),0) AS total FROM 포인트 WHERE 회원_id=%s",
        (member_id,),
    )
    return int(row["total"]) if row else 0


def add_points(member_id: int, points: int, kind="적립"):
    execute(
        """
        INSERT INTO 포인트(회원_id, 유형, 포인트, 발생일시)
        VALUES(%s, %s, %s, NOW())
        """,
        (member_id, kind, int(points)),
    )


def recalc_member_grade(member_id: int):
    total = get_member_points(member_id)

    grade = fetch_one(
        """
        SELECT 등급_id
        FROM 등급
        WHERE 최소포인트 <= %s
        ORDER BY 최소포인트 DESC
        LIMIT 1
        """,
        (total,),
    )

    if grade:
        execute(
            "UPDATE 회원 SET 등급_id=%s WHERE 회원_id=%s",
            (grade["등급_id"], member_id),
        )
