from decimal import Decimal

RATES = {"EUR":Decimal("1.00"), "RON":Decimal("0.20"), "USD":Decimal("0.92"), "GBP":Decimal("1.15")}

def to_eur(value, currency):
    rate = RATES.get(currency.upper(), Decimal("1.00"))
    return Decimal(str(value)) * rate

def keep_under_39_eur(value, currency):
    return to_eur(value, currency) <= Decimal("39.00")
