import pytest
import algosdk

from algopytest import (
    dummy_function,
    payment_transaction,
    smart_signature_transaction,    
    group_elem,
    suggested_params
)

TMPL_FEE = 1000
TMPL_PERIOD = 50
TMPL_AMOUNT = 2_000_000
TMPL_DURATION = 50
TMPL_LEASE = "passwordpasswordpasswordpassword"

def round_down(n, k):
    """Round down the number ``n`` to the nearest multiple of ``k``."""
    return n - (n % k)

def test_pull_payment(smart_signature, owner, user1):
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    params.first = round_down(params.first, TMPL_PERIOD)
    params.last = params.first + TMPL_DURATION
    
    _, txn = group_elem(payment_transaction)(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=TMPL_LEASE, params=params)
    smart_signature_transaction(smart_signature, txn)

def test_pull_payment_raises(smart_signature, owner, user1):
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    # The first valid round is no longer a multiple of `TMPL_PERIOD` which will cause the failure
    params.first = round_down(params.first, TMPL_PERIOD) + 1
    params.last = params.first + TMPL_DURATION
    
    _, txn = group_elem(payment_transaction)(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=TMPL_LEASE, params=params)

    with pytest.raises(algosdk.error.AlgodHTTPError, match=r'transaction .* invalid : transaction .* rejected by logic'):
        smart_signature_transaction(smart_signature, txn)
    

def test_dummy_function():
    assert dummy_function() < 420
