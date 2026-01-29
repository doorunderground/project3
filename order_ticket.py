# order_ticket.py
from db import get_conn

def create_ticket_order(member_id, ticket_id, final_price):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 이용권 구매
            cur.execute(
                """
                INSERT INTO 이용권구매내역
                (회원_id, 이용권_id, 최종결제금액, 구매일시)
                VALUES(%s, %s, %s, NOW())
                """,
                (member_id, ticket_id, final_price),
            )
            buy_id = cur.lastrowid

            # 주문접수
            cur.execute(
                """
                INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                VALUES('TICKET', %s, %s, '대기')
                """,
                (buy_id, member_id),
            )

        conn.commit()
        return buy_id

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
