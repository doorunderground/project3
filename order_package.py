# order_package.py
from db import get_conn

def create_package_order(member_id, package_id, final_price):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO 패키지구매
                (구매일시, 회원_id, 패키지_id, 최종결제금액)
                VALUES(NOW(), %s, %s, %s)
                """,
                (member_id, package_id, final_price),
            )
            pk_id = cur.lastrowid

            cur.execute(
                """
                INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                VALUES('PACKAGE', %s, %s, '대기')
                """,
                (pk_id, member_id),
            )

        conn.commit()
        return pk_id

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
