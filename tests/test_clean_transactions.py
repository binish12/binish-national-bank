from src.transformation.cleaning_rules import clean_amount, clean_transaction_type


def test_clean_amount_valid_float():
    assert clean_amount(45.67) == 45.67


def test_clean_amount_currency_string():
    assert clean_amount("$45.67") == 45.67


def test_clean_amount_none():
    assert clean_amount(None) is None


def test_clean_amount_empty_string():
    assert clean_amount("") is None


def test_clean_transaction_type_valid():
    assert clean_transaction_type("purchase") == "purchase"


def test_clean_transaction_type_needs_normalizing():
    assert clean_transaction_type("PURCHASE ") == "purchase"


def test_clean_transaction_type_invalid():
    assert clean_transaction_type("unknown") is None
