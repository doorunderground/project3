# price.py

def normalize_rate(rate):
    '''
        할인율 5%
    '''
    if rate is None:
        return 0.0
    r = float(rate)
    return r / 100.0 if r > 1 else r
    # input        r>1?        result
    #  5           OK           0.05
    # 0.05         NO           0.05


def calc_final(subtotal, rate):
    '''
        정가합계(subtotal)와 할인율(rate)을 받아
        (할인금액, 최종결제금액) 반환
    '''
    r = normalize_rate(rate)
    discount = int(round(subtotal * r))
    final = max(0, int(subtotal - discount))
    return discount, final
