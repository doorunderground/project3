from db import fetch_all,execute

def cart_add(member_id, food_id, qty):
    execute(
        """
        INSERT INTO 장바구니(회원_id, 음식_id, 수량)
        VALUES(%s, %s, %s)
        ON DUPLICATE KEY UPDATE 수량 = 수량 + VALUES(수량)
        """,
        (member_id, food_id, int(qty)),
    )

def cart_list(member_id):
    return fetch_all(
        """
        SELECT c.음식_id, f.음식이름, f.가격 AS 단가, c.수량,
               (f.가격 * c.수량) AS 라인금액, c.담은일시
        FROM 장바구니 c
        JOIN 음식 f ON c.음식_id = f.음식_id
        WHERE c.회원_id=%s
        ORDER BY c.담은일시 DESC
        """,
        (member_id,),
    )

def cart_update_qty(member_id, food_id, qty):
    if int(qty) <= 0:
        execute("DELETE FROM 장바구니 WHERE 회원_id=%s AND 음식_id=%s", (member_id, food_id))
    else:
        execute("UPDATE 장바구니 SET 수량=%s WHERE 회원_id=%s AND 음식_id=%s", (int(qty), member_id, food_id))

def cart_clear(member_id):
    execute("DELETE FROM 장바구니 WHERE 회원_id=%s", (member_id,))