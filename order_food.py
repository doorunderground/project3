# order_food.py
from db import get_conn

def create_food_order(member_id, cart_rows, subtotal, discount, final):
    """
    음식 주문 생성
    - 음식주문_헤더
    - 음식주문_상세
    - 주문접수
    - 장바구니 비우기
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1) 주문 헤더
            cur.execute(
                """
                INSERT INTO 음식주문_헤더
                (회원_id, 주문일시, 정가합계, 할인금액, 최종결제금액)
                VALUES(%s, NOW(), %s, %s, %s)
                """,
                (member_id, subtotal, discount, final),
            )
            order_id = cur.lastrowid

            # 2) 주문 상세
            for r in cart_rows:
                cur.execute(
                    """
                    INSERT INTO 음식주문_상세
                    (주문_id, 음식_id, 수량, 단가, 라인금액)
                    VALUES(%s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        r["음식_id"],
                        int(r["수량"]),
                        int(r["단가"]),
                        int(r["라인금액"]),
                    ),
                )

            # 3) 주문접수(직원 큐)
            cur.execute(
                """
                INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                VALUES('FOOD', %s, %s, '대기')
                """,
                (order_id, member_id),
            )

            # 4) 장바구니 비우기
            cur.execute(
                "DELETE FROM 장바구니 WHERE 회원_id=%s",
                (member_id,),
            )

        conn.commit()
        return order_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
