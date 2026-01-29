# staff.py
from db import fetch_all, fetch_one, execute

def fetch_all_orders():
    sql = """
    SELECT
      q.주문접수_id,
      q.주문유형,
      q.참조_id AS 주문_id,
      q.회원_id,
      m.회원명,
      q.요청일시,
      q.상태,
      q.처리일시,
      q.메모,
      h.최종결제금액 AS 금액,
      GROUP_CONCAT(CONCAT(f.음식이름,'x',d.수량) SEPARATOR ', ') AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id=m.회원_id
    JOIN 음식주문_헤더 h ON q.주문유형='FOOD' AND q.참조_id=h.주문_id
    JOIN 음식주문_상세 d ON h.주문_id=d.주문_id
    JOIN 음식 f ON d.음식_id=f.음식_id
    GROUP BY q.주문접수_id

    UNION ALL

    SELECT
      q.주문접수_id,
      q.주문유형,
      q.참조_id AS 주문_id,
      q.회원_id,
      m.회원명,
      q.요청일시,
      q.상태,
      q.처리일시,
      q.메모,
      p.최종결제금액 AS 금액,
      t.이용권명 AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id=m.회원_id
    JOIN 이용권구매내역 p ON q.주문유형='TICKET' AND q.참조_id=p.이용권구매_id
    JOIN 이용권 t ON p.이용권_id=t.이용권_id

    UNION ALL

    SELECT
      q.주문접수_id,
      q.주문유형,
      q.참조_id AS 주문_id,
      q.회원_id,
      m.회원명,
      q.요청일시,
      q.상태,
      q.처리일시,
      q.메모,
      pk.최종결제금액 AS 금액,
      CONCAT(k.패키지명,' / ',
             COALESCE(f.음식이름,'음식없음'),' + ',
             COALESCE(t.이용권명,'이용권없음')) AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id=m.회원_id
    JOIN 패키지구매 pk ON q.주문유형='PACKAGE' AND q.참조_id=pk.패키지구매_id
    JOIN 패키지 k ON pk.패키지_id=k.패키지_id
    LEFT JOIN 음식 f ON k.음식_id=f.음식_id
    LEFT JOIN 이용권 t ON k.이용권_id=t.이용권_id

    ORDER BY 요청일시 DESC
    """
    return fetch_all(sql)

def update_order_status(order_receipt_id, status, memo=None):
    if status == "완료":
        execute(
            """
            UPDATE 주문접수
            SET 상태=%s, 처리일시=NOW(), 메모=%s
            WHERE 주문접수_id=%s
            """,
            (status, memo, order_receipt_id),
        )
    else:
        execute(
            """
            UPDATE 주문접수
            SET 상태=%s, 메모=%s
            WHERE 주문접수_id=%s
            """,
            (status, memo, order_receipt_id),
        )
