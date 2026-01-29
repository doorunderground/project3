# pricing.py

def normalize_rate(rate):
    """
    할인율이 5.00(%) 또는 0.05(비율) 모두 지원
    """
    if rate is None:
        return 0.0
    r = float(rate)
    return r / 100.0 if r > 1 else r


def calc_final(subtotal, rate):
    """
    정가합계(subtotal)와 할인율(rate)을 받아
    (할인금액, 최종결제금액) 반환
    """
    r = normalize_rate(rate)
    discount = int(round(subtotal * r))
    final = max(0, int(subtotal - discount))
    return discount, final
