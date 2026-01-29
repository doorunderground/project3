import streamlit as st
import pandas as pd

from db import fetch_all, fetch_one
from staff import fetch_all_orders, update_order_status
from cart import cart_add, cart_list, cart_clear
from order_food import create_food_order
from member import get_member_info, get_member_points, add_points, recalc_member_grade
from price import calc_final




#############################################
#    DB :  "문지하  " 
#   입력:  "문지하"
#   "문지하 " == "문지하"   ->  False
##############################################
def clean_name(s: str) -> str:
    if s is None:
        return ""
    return str(s).replace("\u00A0", " ").strip()


# 로그인 안 했으면 이 페이지에서 더 이상 실행하지 마라
def ensure_member():
    if not st.session_state.member_id:
        st.error("먼저 메인 화면에서 회원 인증을 해주세요.")
        st.stop()

##############################################
#┌──────┬──────────────┬──────┐
#│ 메인 │   회원정보    │ 로그 │
#└──────┴──────────────┴──────┘
##############################################
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
                rate = info.get("할인율") or 0
                rate_percent = rate if rate <= 1 else rate / 100
                
                st.caption(
                    f'현재 회원: {info["회원명"]} (ID {info["회원_id"]}) / '
                    f'등급 {info.get("등급이름","-")} / 할인 {rate_percent*100:.1f}%'
                )
    with c3:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.member_id = None
            st.session_state.page = "HOME"
            st.rerun()


# ============================================================
# start
# ============================================================
st.set_page_config(page_title="PC방 주문 시스템", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "HOME"
if "member_id" not in st.session_state:
    st.session_state.member_id = None

st.title("PC방 메인 화면")

# ============================================================
# HOME: 회원번호 + 이름 확인
# ============================================================
if st.session_state.page == "HOME":
    st.subheader("1) 회원 정보 입력 (회원번호 + 이름 확인)")

    with st.form("login_form", clear_on_submit=False):
        member_id_in = st.number_input("회원번호", min_value=1, step=1)
        member_name_in = st.text_input("회원명", placeholder="예: 문지하")
        login_btn = st.form_submit_button("확인")

    if login_btn:
        row = fetch_one("SELECT 회원_id, 회원명 FROM 회원 WHERE 회원_id=%s", (int(member_id_in),))
        if not row:
            st.session_state.member_id = None
            st.error("해당 회원번호가 존재하지 않습니다.")
        else:
            db_name = clean_name(row["회원명"])
            in_name = clean_name(member_name_in)
            if db_name == in_name:
                st.session_state.member_id = int(member_id_in)
                info = get_member_info(st.session_state.member_id)
                pts = get_member_points(st.session_state.member_id)
                rate = info.get("할인율") or 0
                rate_percent = rate if rate <= 1 else rate / 100

                st.success("회원 정보 확인 완료 ✅")
                st.info(
                    f'👤 회원: {info["회원명"]} (ID: {info["회원_id"]})\n\n'
                    f'🏷️ 등급: {info.get("등급이름","(없음)")} / 할인율: {rate_percent*100:.1f}%\n\n'
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

# ============================================================
# FOOD: 장바구니 담기/수정/주문확정(헤더+상세+주문접수)
# ============================================================
if st.session_state.page == "FOOD":
    ensure_member()
    top_bar()

    st.subheader("2) 음식 주문 시스템 (장바구니)")

    foods = fetch_all("SELECT 음식_id, 음식이름, 가격 FROM 음식 ORDER BY 음식_id")
    if not foods:
        st.warning("음식 테이블 데이터가 없습니다.")
        st.stop()

    st.dataframe(pd.DataFrame(foods), use_container_width=True, hide_index=True)

    label_map = {f'{r["음식_id"]} - {r["음식이름"]} ({r["가격"]}원)': r for r in foods}
    choice = st.selectbox("메뉴 선택", list(label_map.keys()))
    qty = st.number_input("수량", 1, 50, 1)

    col_add, col_clear = st.columns([1, 1])
    with col_add:
        if st.button("장바구니 담기", type="secondary", use_container_width=True):
            selected = label_map[choice]
            cart_add(st.session_state.member_id, selected["음식_id"], qty)
            st.success("장바구니에 담았습니다 ✅")
            st.rerun()
    with col_clear:
        if st.button("장바구니 비우기", use_container_width=True):
            cart_clear(st.session_state.member_id)
            st.rerun()

    st.divider()
    st.subheader("🧺 장바구니")

    cart_rows = cart_list(st.session_state.member_id)
    if not cart_rows:
        st.info("장바구니가 비어있습니다.")
        st.stop()

    cart_df = pd.DataFrame(cart_rows)
    st.dataframe(cart_df, use_container_width=True, hide_index=True)


    # 합계/할인
    subtotal = int(cart_df["라인금액"].sum())
    member = get_member_info(st.session_state.member_id)
    discount, final = calc_final(subtotal, member.get("할인율") if member else 0)

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가합계", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")


    if st.button("주문요청 전송(장바구니 전체)", type="primary"):
        try:
            order_id = create_food_order(
                st.session_state.member_id,
                cart_rows,
                subtotal,
                discount,
                final,
            )

            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("4. 회원님의 음식 주문(장바구니)이 완료되었습니다 ✅")
            st.info("📥 직원용 '주문 접수 화면'에서 주문 상세가 보입니다.")
        except Exception as e:
            st.error(f"주문 실패: {e}")


# ============================================================
# TICKET: 이용권 구매 + 주문접수
# ============================================================
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
    discount, final = calc_final(subtotal, member.get("할인율") if member else 0)

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")

    from order_ticket import create_ticket_order

    if st.button("구매요청 전송", type="primary"):
        try:
            buy_id = create_ticket_order(
                st.session_state.member_id,
                selected["이용권_id"],
                final,
            )

            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("이용권 구매가 완료되었습니다 ✅")
        except Exception as e:
            st.error(f"구매 실패: {e}")

# ============================================================
# PACKAGE: 패키지 구매 + 주문접수
# ============================================================
if st.session_state.page == "PACKAGE":
    ensure_member()
    top_bar()

    st.subheader("2) 패키지 구매 시스템")

    packages = fetch_all(
        """
        SELECT p.패키지_id, p.패키지명, p.가격,
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
    discount, final = calc_final(subtotal, member.get("할인율") if member else 0)

    st.subheader("3) 최종 가격 확인(등급 할인 적용)")
    a, b, c = st.columns(3)
    a.metric("정가", f"{subtotal:,}원")
    b.metric("할인", f"-{discount:,}원")
    c.metric("최종결제금액", f"{final:,}원")

    from order_package import create_package_order

    if st.button("구매요청 전송", type="primary"):
        try:
            pk_id = create_package_order(
                st.session_state.member_id,
                selected["패키지_id"],
                final,
            )

            earned = int(final * 0.01)
            if earned > 0:
                add_points(st.session_state.member_id, earned, "적립")
                recalc_member_grade(st.session_state.member_id)

            st.success("패키지 구매가 완료되었습니다 ✅")
        except Exception as e:
            st.error(f"구매 실패: {e}")

# ============================================================
# STAFF: 직원용 주문 접수 화면 (전체 테이블 표시)
# ============================================================
if st.session_state.page == "STAFF":
    top_bar()

    st.subheader("📥 주문 접수 화면(직원용) - 전체 주문")

    rows = fetch_all_orders()
    if not rows:
        st.info("접수된 주문이 없습니다.")
        st.stop()

    df = pd.DataFrame(rows)

    show_cols = [
        "주문접수_id",
        "주문유형",
        "회원명",
        "요청일시",
        "구성",
        "금액",
        "상태",
        "메모"
    ]

    st.dataframe(
        df[show_cols],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ---------------------------
    # 상태 변경(업데이트)
    # ---------------------------
    st.subheader("상태 변경(업데이트)")

    c1, c2 = st.columns([2, 3])

    with c1:
        order_id = st.number_input("주문접수_id", min_value=1, step=1)

    with c2:
        new_status = st.selectbox("변경할 상태", ["대기", "처리중", "완료", "취소"])

    memo = st.text_input(
        "메모(선택)",
        placeholder="예: 재고 부족 / 계란 (완숙) 등"
    )
    
    if st.button("상태 업데이트", type="primary"):
        update_order_status(
        order_receipt_id=int(order_id),
        status=new_status,
        memo=memo or None
        )
        st.success("주문 상태가 업데이트되었습니다 ✅")
        st.rerun()


