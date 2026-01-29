# order_food.py
'''
    장바구니에 담긴 음식들을
    하나의 '음식주문'으로 확정하고
    (헤더 + 상세 + 직원용 접수)까지 만듦
'''

from db import get_conn

def create_food_order(member_id, cart_rows, subtotal, discount, final):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1) 음식주문_헤더
            cur.execute(
                """
                INSERT INTO 음식주문_헤더
                (회원_id, 주문일시, 정가합계, 할인금액, 최종결제금액)
                VALUES(%s, NOW(), %s, %s, %s)
                """,
                (member_id, subtotal, discount, final),
            )
            order_id = cur.lastrowid

            # 2) 음식주문_상세
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

            # 3) 주문접수(직원)
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
