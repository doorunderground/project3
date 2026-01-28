import streamlit as st
import pandas as pd
import pymysql

# =========================
# DB 연결 (형님 방식)
# =========================
def get_conn():
    return pymysql.connect(
        user="root",
        password="1234",
        host="127.0.0.1",
        databasse="pc",
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

def fetch_all(sql, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()

def execute(sql, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# =========================
# 유틸/로직
# =========================
def clean_name(s: str) -> str:
    if s is None:
        return ""
    return s.replace("\u00A0", " ").strip()  # NBSP 제거 + trim

def normalize_rate(rate):
    # 5.00(%) or 0.05 둘 다 대응
    if rate is None:
        return 0.0
    r = float(rate)
    return r / 100.0 if r > 1 else r

def calc_final(subtotal, rate):
    r = normalize_rate(rate)
    discount = int(round(subtotal * r))
    final = max(0, int(subtotal - discount))
    return discount, final

def get_member_info(member_id):
    rows = fetch_all(
        """
        SELECT m.회원_id, m.회원명, m.가입일시, m.연령대,
               g.등급_id, g.등급이름, g.할인율, g.최소포인트
        FROM 회원 m
        LEFT JOIN 등급 g ON m.등급_id = g.등급_id
        WHERE m.회원_id=%s
        """,
        (member_id,)
    )
    return rows[0] if rows else None

def get_member_points(member_id):
    rows = fetch_all(
        "SELECT COALESCE(SUM(포인트),0) AS total FROM 포인트 WHERE 회원_id=%s",
        (member_id,)
    )
    return int(rows[0]["total"]) if rows else 0

def add_points(member_id, points, kind="적립"):
    execute(
        "INSERT INTO 포인트(회원_id, 유형, 포인트, 발생일시) VALUES(%s,%s,%s,NOW())",
        (member_id, kind, int(points)),
    )

def recalc_member_grade(member_id):
    total = get_member_points(member_id)
    grade = fetch_all(
        """
        SELECT 등급_id
        FROM 등급
        WHERE 최소포인트 <= %s
        ORDER BY 최소포인트 DESC
        LIMIT 1
        """,
        (total,)
    )
    if grade:
        execute("UPDATE 회원 SET 등급_id=%s WHERE 회원_id=%s", (grade[0]["등급_id"], member_id))

def ensure_member():
    if not st.session_state.member_id:
        st.error("먼저 메인 화면에서 회원 인증을 해주세요.")
        st.stop()

def top_bar():
    c1, c2, c3 = st.columns([1.2, 2.8, 1.2])
    with c1:
        if st.button("← 메인", use_container_width=True):
            st.session_state.page = "HOME"
            st.rerun()
    with c2:
        if st.session_state.member_id:
            info = get_member_info(st.session_state.member_id)
            if info:
                rate = normalize_rate(info.get("할인율"))
                st.caption(f'현재 회원: {info["회원명"]} (ID {info["회원_id"]}) / 등급 {info.get("등급이름","-")} / 할인 {rate*100:.1f}%')
    with c3:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.member_id = None
            st.session_state.page = "HOME"
            st.rerun()

# =========================
# 주문접수(직원 큐) 상세 조회용 (UNION)
# =========================
def fetch_queue_detail(status):
    sql = """
    SELECT
      q.주문접수_id, q.주문유형, q.참조_id, q.회원_id, m.회원명,
      q.요청일시, q.상태, q.처리일시, q.메모,
      f.음식이름 AS 상품명,
      o.수량 AS 수량,
      o.최종결제금액 AS 금액,
      NULL AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id = m.회원_id
    JOIN 음식주문 o ON q.주문유형='FOOD' AND q.참조_id = o.주문_id
    JOIN 음식 f ON o.음식_id = f.음식_id
    WHERE q.상태=%s

    UNION ALL

    SELECT
      q.주문접수_id, q.주문유형, q.참조_id, q.회원_id, m.회원명,
      q.요청일시, q.상태, q.처리일시, q.메모,
      t.이용권명 AS 상품명,
      1 AS 수량,
      p.최종결제금액 AS 금액,
      NULL AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id = m.회원_id
    JOIN 이용권구매내역 p ON q.주문유형='TICKET' AND q.참조_id = p.이용권구매_id
    JOIN 이용권 t ON p.이용권_id = t.이용권_id
    WHERE q.상태=%s

    UNION ALL

    SELECT
      q.주문접수_id, q.주문유형, q.참조_id, q.회원_id, m.회원명,
      q.요청일시, q.상태, q.처리일시, q.메모,
      k.패키지명 AS 상품명,
      1 AS 수량,
      pk.최종결제금액 AS 금액,
      CONCAT(COALESCE(ff.음식이름,'음식없음'),' + ',COALESCE(tt.이용권명,'이용권없음')) AS 구성
    FROM 주문접수 q
    JOIN 회원 m ON q.회원_id = m.회원_id
    JOIN 패키지구매 pk ON q.주문유형='PACKAGE' AND q.참조_id = pk.패키지구매_id
    JOIN 패키지 k ON pk.패키지_id = k.패키지_id
    LEFT JOIN 음식 ff ON k.음식_id = ff.음식_id
    LEFT JOIN 이용권 tt ON k.이용권_id = tt.이용권_id
    WHERE q.상태=%s

    ORDER BY 요청일시 DESC
    """
    return fetch_all(sql, (status, status, status))

# =========================
# 앱 설정/상태
# =========================
st.set_page_config(page_title="PC방 주문 시스템", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "HOME"
if "member_id" not in st.session_state:
    st.session_state.member_id = None

st.title("PC방 메인 화면")

# =========================
# HOME: 회원 인증 + 이동 버튼 + 직원 화면 버튼
# =========================
if st.session_state.page == "HOME":
    st.subheader("1) 회원 정보 입력 (회원번호 + 이름 확인)")

    with st.form("login_form", clear_on_submit=False):
        member_id_in = st.number_input("회원번호", min_value=1, step=1)
        member_name_in = st.text_input("회원명", placeholder="예: 문지하")
        login_btn = st.form_submit_button("확인")

    if login_btn:
        rows = fetch_all("SELECT 회원_id, 회원명 FROM 회원 WHERE 회원_id=%s", (int(member_id_in),))
        if not rows:
            st.session_state.member_id = None
            st.error("해당 회원번호가 존재하지 않습니다.")
        else:
            db_name = clean_name(rows[0]["회원명"])
            in_name = clean_name(member_name_in)
            if db_name == in_name:
                st.session_state.member_id = int(member_id_in)
                info = get_member_info(st.session_state.member_id)
                pts = get_member_points(st.session_state.member_id)
                rate = normalize_rate(info.get("할인율"))
                st.success("회원 정보 확인 완료 ✅")
                st.info(
                    f'👤 회원: {info["회원명"]} (ID: {info["회원_id"]})\n\n'
                    f'🏷️ 등급: {info.get("등급이름","(없음)")} / 할인율: {rate*100:.1f}%\n\n'
                    f'⭐ 누적 포인트: {pts}'
                )
            else:
                st.session_state.member_id = None
                st.error("회원번호와 회원명이 일치하지 않습니다. 다시 확인해주세요.")

    st.divider()
    st.subheader("상품 조회 및 구매")

    disabled = st.session_state.member_id is None
    c1, c2, c3 = st.columns(3)
    if c1.button("음식 구매", use_container_width=True, disabled=disabled):
        st.session_state.page = "FOOD"
        st.rerun()
    if c2.button("이용권 구매", use_container_width=True, disabled=disabled):
        st.session_state.page = "TICKET"
        st.rerun()
    if c3.button("패키지 구매", use_container_width=True, disabled=disabled):
        st.session_state.page = "PACKAGE"
        st.rerun()

    st.divider()
    st.subheader("직원용")
    if st.button("📥 주문 접수 화면(직원용)", use_container_width=True):
        st.session_state.page = "STAFF"
        st.rerun()

# =========================
# FOOD: 음식 주문 + 주문접수 insert (트랜잭션)
# =========================
if st.session_state.page == "FOOD":
    ensure_member()
    top_bar()
    st.subheader("2) 음식 주문 시스템")

    foods = fetch_all("SELECT 음식_id, 음식이름, 가격 FROM 음식 ORDER BY 음식_id")
    if not foods:
        st.warning("음식 테이블 데이터가 없습니다.")
        st.stop()

    st.dataframe(pd.DataFrame(foods), use_container_width=True, hide_index=True)

    label_map = {f'{r["음식_id"]} - {r["음식이름"]} ({r["가격"]}원)': r for r in foods}
    choice = st.selectbox("메뉴 선택", list(label_map.keys()))
    qty = st.number_input("수량", 1, 50, 1)

    selected = label_map[choice]
    subtotal = int(selected["가격"]) * int(qty)

    member = get_member_info(st.session_state.member_id)
    discount, final = calc_final(subtotal, member.get("할인율"))

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")

    if st.button("주문요청 전송", type="primary"):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # 1) 음식주문 기록
                cur.execute(
                    """
                    INSERT INTO 음식주문(회원_id, 음식_id, 주문일시, 수량, 최종결제금액)
                    VALUES(%s, %s, NOW(), %s, %s)
                    """,
                    (st.session_state.member_id, selected["음식_id"], int(qty), int(final))
                )
                order_id = cur.lastrowid

                # 2) 주문접수(직원 큐) 기록
                cur.execute(
                    """
                    INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                    VALUES('FOOD', %s, %s, '대기')
                    """,
                    (order_id, st.session_state.member_id)
                )

            conn.commit()

            # (옵션) 포인트 1% 적립 + 등급 갱신
            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("4. 회원님의 음식 주문이 완료되었습니다 ✅")
            st.info("📥 직원용 '주문 접수 화면'에서 방금 주문이 대기 상태로 들어갑니다.")
        except Exception as e:
            conn.rollback()
            st.error(f"주문 실패: {e}")
        finally:
            conn.close()

# =========================
# TICKET: 이용권 구매 + 주문접수 insert
# =========================
if st.session_state.page == "TICKET":
    ensure_member()
    top_bar()
    st.subheader("2) 이용권 구매 시스템")

    tickets = fetch_all("SELECT 이용권_id, 이용권명, 가격 FROM 이용권 ORDER BY 이용권_id")
    if not tickets:
        st.warning("이용권 테이블 데이터가 없습니다.")
        st.stop()

    st.dataframe(pd.DataFrame(tickets), use_container_width=True, hide_index=True)

    label_map = {f'{r["이용권_id"]} - {r["이용권명"]} ({r["가격"]}원)': r for r in tickets}
    choice = st.selectbox("이용권 선택", list(label_map.keys()))
    selected = label_map[choice]

    subtotal = int(selected["가격"])
    member = get_member_info(st.session_state.member_id)
    discount, final = calc_final(subtotal, member.get("할인율"))

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")

    if st.button("구매요청 전송", type="primary"):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO 이용권구매내역(회원_id, 이용권_id, 최종결제금액, 구매일시)
                    VALUES(%s, %s, %s, NOW())
                    """,
                    (st.session_state.member_id, selected["이용권_id"], int(final))
                )
                buy_id = cur.lastrowid

                cur.execute(
                    """
                    INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                    VALUES('TICKET', %s, %s, '대기')
                    """,
                    (buy_id, st.session_state.member_id)
                )

            conn.commit()

            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("4. 회원님의 이용권 구매가 완료되었습니다 ✅")
            st.info("📥 직원용 '주문 접수 화면'에서 방금 구매가 대기 상태로 들어갑니다.")
        except Exception as e:
            conn.rollback()
            st.error(f"구매 실패: {e}")
        finally:
            conn.close()

# =========================
# PACKAGE: 패키지 구매 + 주문접수 insert
# =========================
if st.session_state.page == "PACKAGE":
    ensure_member()
    top_bar()
    st.subheader("2) 패키지 구매 시스템")

    packages = fetch_all(
        """
        SELECT p.패키지_id, p.패키지명, p.연령대, p.가격,
               p.음식_id, f.음식이름,
               p.이용권_id, t.이용권명
        FROM 패키지 p
        LEFT JOIN 음식 f ON p.음식_id = f.음식_id
        LEFT JOIN 이용권 t ON p.이용권_id = t.이용권_id
        ORDER BY p.패키지_id
        """
    )
    if not packages:
        st.warning("패키지 테이블 데이터가 없습니다.")
        st.stop()

    st.dataframe(pd.DataFrame(packages), use_container_width=True, hide_index=True)

    label_map = {}
    for r in packages:
        food_name = r["음식이름"] if r["음식이름"] else "음식없음"
        ticket_name = r["이용권명"] if r["이용권명"] else "이용권없음"
        label = f'{r["패키지_id"]} - {r["패키지명"]} ({r["가격"]}원) / 구성: {food_name} + {ticket_name}'
        label_map[label] = r

    choice = st.selectbox("패키지 선택", list(label_map.keys()))
    selected = label_map[choice]

    subtotal = int(selected["가격"])
    member = get_member_info(st.session_state.member_id)
    discount, final = calc_final(subtotal, member.get("할인율"))

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")

    if st.button("구매요청 전송", type="primary"):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO 패키지구매(구매일시, 회원_id, 패키지_id, 최종결제금액)
                    VALUES(NOW(), %s, %s, %s)
                    """,
                    (st.session_state.member_id, selected["패키지_id"], int(final))
                )
                pk_id = cur.lastrowid

                cur.execute(
                    """
                    INSERT INTO 주문접수(주문유형, 참조_id, 회원_id, 상태)
                    VALUES('PACKAGE', %s, %s, '대기')
                    """,
                    (pk_id, st.session_state.member_id)
                )

            conn.commit()

            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("4. 회원님의 패키지 구매가 완료되었습니다 ✅")
            st.info("📥 직원용 '주문 접수 화면'에서 방금 구매가 대기 상태로 들어갑니다.")
        except Exception as e:
            conn.rollback()
            st.error(f"구매 실패: {e}")
        finally:
            conn.close()

# =========================
# STAFF: 직원용 주문 큐 + 상세 + 상태 업데이트(테이블 UPDATE)
# =========================
if st.session_state.page == "STAFF":
    top_bar()
    st.subheader("📥 주문 접수 화면(직원용) - 상세 포함")

    status = st.selectbox("상태 필터", ["대기", "처리중", "완료", "취소"], index=0)

    rows = fetch_queue_detail(status)
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("해당 상태의 주문이 없습니다.")
    else:
        # 보기 좋게 컬럼 정리
        show_cols = ["주문접수_id","주문유형","회원_id","회원명","요청일시","상품명","구성","수량","금액","상태","처리일시","메모","참조_id"]
        show_cols = [c for c in show_cols if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("상태 변경(업데이트)")

    c1, c2 = st.columns([1, 2])
    with c1:
        pick_id = st.number_input("주문접수_id", min_value=1, step=1)
    with c2:
        new_status = st.selectbox("변경할 상태", ["대기", "처리중", "완료", "취소"])

    memo = st.text_input("메모(선택)", placeholder="예: 3번 PC로 배달 / 재고부족 등")

    if st.button("상태 업데이트", type="primary"):
        if new_status == "완료":
            execute(
                "UPDATE 주문접수 SET 상태=%s, 처리일시=NOW(), 메모=%s WHERE 주문접수_id=%s",
                (new_status, memo if memo else None, int(pick_id))
            )
        else:
            execute(
                "UPDATE 주문접수 SET 상태=%s, 메모=%s WHERE 주문접수_id=%s",
                (new_status, memo if memo else None, int(pick_id))
            )
        st.success("주문접수 테이블 상태가 업데이트되었습니다 ✅")
        st.rerun()
