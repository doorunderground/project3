# staff.py
'''
    주문유형       |          Table
      FOOD               음식주문_헤더/상세
     TICKET               이용권구매내역
     PACKAGE                패키지구매
    
    음식주문 1건 -> 직원 화면에서 '한 줄로' 보여줘야함 
    직원은 각각의 테이블에서 값들을 받아와야함.
    -> UNION ALL
'''

from db import fetch_all, fetch_one, execute

def fetch_all_orders():
    '''
    주문접수 (q)
    └─ 주문접수_id (1)
    └─ 주문유형 = 'FOOD'
    └─ 참조_id = 15  ─────────────┐
                                  │
    음식주문_헤더 (h)              │
    └─ 주문_id = 15 ◀─────────────┘
    └─ 최종결제금액 = 7500

    음식주문_상세 (d)
    ├─ (주문_id=15, 음식_id=1, 수량=2)
    ├─ (주문_id=15, 음식_id=3, 수량=1)

    음식 (f)
    ├─ 음식_id=1 → 라면
    ├─ 음식_id=3 → 콜라
    '''
    
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


'''
주문접수 1건을 기준으로 
음식 주문 + (이용권, 패키지)을 끌어와 다시 1줄로 만드는 구조

  [주문접수 q]
┌──────────────┐
│ 주문접수_id  │ 101
│ 주문유형     │ FOOD
│ 참조_id      │ 15   ───────────────┐
│ 회원_id      │ 3                   │
└──────────────┘                     │
                                     │
                                      ▼
                           [음식주문_헤더 h]
                           ┌──────────────┐
                           │ 주문_id      │  15
                           │ 최종결제금액 │  7500
                           └──────────────┘
                                      │
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
     [음식주문_상세 d]                             [음식주문_상세 d]
┌──────────────┐                             ┌──────────────┐
│ 주문_id      │ 15                          │ 주문_id      │ 15
│ 음식_id      │ 1                           │ 음식_id      │ 3
│ 수량         │ 2                           │ 수량         │ 1
└──────────────┘                             └──────────────┘
        │                                             │
        ▼                                             ▼
   [음식 f]                                     [음식 f]
┌──────────────┐                           ┌──────────────┐
│ 음식_id      │ 1                         │ 음식_id      │  3
│ 음식이름     │ 라면                      │ 음식이름      │ 콜라
└──────────────┘                           └──────────────┘


JOIN을 하면?

(아직 GROUP BY 전)

주문접수_id | 음식이름 | 수량
--------------------------------
101          | 라면     | 2
101          | 콜라     | 1


(GROUP BY)

주문접수_id = 101
┌──────────────┐
│ 라면 x 2     │     concat
│ 콜라 x 1     │
└──────────────┘


┌────────────┬────────┬───────────────┬───────┐
│ 주문접수_id│ 회원명  │ 구성          │  금액 │
├────────────┼────────┼───────────────┼───────┤
│ 101        │ 문지하 │ 라면x2, 콜라x1 │ 7500  │
└────────────┴────────┴───────────────┴───────┘


'''