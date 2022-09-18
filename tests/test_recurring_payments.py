import pytest
import algosdk

from algopytest import (
    payment_transaction,
    smart_signature_transaction,    
    txn_elem,
    group_transaction,
    suggested_params
)

TMPL_FEE = 1000
TMPL_PERIOD = 50
TMPL_AMOUNT = 2_000_000
TMPL_DURATION = 50
TMPL_LEASE = "fillerfillerfillerfillerfiller"

def round_down(n, k):
    """Round down the number ``n`` to the nearest multiple of ``k``."""
    return n - (n % k)

def test_pull_payment_single_receiver(smart_signature, owner, user1):
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    params.first = round_down(params.first, TMPL_PERIOD)
    params.last = params.first + TMPL_DURATION
    
    _, txn = txn_elem(payment_transaction)(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_0', params=params)
    smart_signature_transaction(smart_signature, txn)

def test_pull_payment_multiple_receiver(smart_signature_two_receivers, owner, user1, user2):
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    params.first = round_down(params.first, TMPL_PERIOD)
    params.last = params.first + TMPL_DURATION
    
    _, txn0 = txn_elem(payment_transaction)(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_0', params=params)
    _, txn1 = txn_elem(payment_transaction)(sender=owner, receiver=user2, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_1', params=params)

    group_transaction(
        txn_elem(smart_signature_transaction)(smart_signature_two_receivers, txn0),
        txn_elem(smart_signature_transaction)(smart_signature_two_receivers, txn1),
    )

def test_pull_payment_raises_invalid_first_round(smart_signature, owner, user1):
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    # The first valid round is no longer a multiple of `TMPL_PERIOD` which will cause the failure
    params.first = round_down(params.first, TMPL_PERIOD) + 1
    params.last = params.first + TMPL_DURATION
    
    _, txn = txn_elem(payment_transaction)(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_0', params=params)

    with pytest.raises(algosdk.error.AlgodHTTPError, match=r'transaction .* invalid : transaction .* rejected by logic'):
        smart_signature_transaction(smart_signature, txn)

