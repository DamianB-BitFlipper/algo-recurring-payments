import pytest
import algosdk

from algopytest import (
    payment_transaction,
    smart_signature_transaction,    
    TxnElemsContext,
    TxnIDContext,
    group_transaction,
    suggested_params,
    transaction_info,
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
    """Test that a single receiver can pull from ``owner`` via their signed ``smart_signature``.

    This test showcases AlgoPytest's context managers ``TxnElemsContext`` and ``TxnIDContext``
    which modify the behavior of any AlgoPytest transaction operators within their blocks. It
    also proves that the transaction sent was signed using the logic (smart) signature."""
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    params.first = round_down(params.first, TMPL_PERIOD)
    params.last = params.first + TMPL_DURATION

    with TxnElemsContext():
        txn = payment_transaction(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_0', params=params)

    with TxnIDContext():
        txn_id, _ = smart_signature_transaction(smart_signature, txn)

    assert 'logicsig' in transaction_info(txn_id)['transaction']['signature']

def test_pull_payment_multiple_receiver(smart_signature_two_receivers, owner, user1, user2):
    """Test that multiple receivers can pull from ``owner`` via their signed ``smart_signature``."""
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    params.first = round_down(params.first, TMPL_PERIOD)
    params.last = params.first + TMPL_DURATION

    with TxnElemsContext():
        txn0 = payment_transaction(sender=owner, receiver=user1, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_0', params=params)
        txn1 = payment_transaction(sender=owner, receiver=user2, amount=TMPL_AMOUNT, lease=f'{TMPL_LEASE}_1', params=params)

        lsig_txn0 = smart_signature_transaction(smart_signature_two_receivers, txn0)
        lsig_txn1 = smart_signature_transaction(smart_signature_two_receivers, txn1)

    group_transaction(lsig_txn0, lsig_txn1)

@pytest.mark.parametrize(
    "invalid_param",
    [
        ({"first-round": 1}),
        ({"lease": f"{TMPL_LEASE}XX"}),
        ({"amount": TMPL_AMOUNT + 1}),
        ({"amount": TMPL_AMOUNT - 1}),        
    ]
)
def test_pull_payment_raises(smart_signature, owner, user1, invalid_param):
    """Test the various failure modes of the smart signature.

    The smart signature should reject any transaction that:
    - has a faulty round validity envelope.
    - has a faulty lease.
    - is pulling too many Algos.
    - is pulling too few Algos."""
    _first_round = invalid_param.get('first-round', 0)
    _lease = invalid_param.get('lease', f"{TMPL_LEASE}_0")
    _amount = invalid_param.get('amount', TMPL_AMOUNT)
    
    params = suggested_params(flat_fee=True, fee=TMPL_FEE)
    # The first valid round is no longer a multiple of `TMPL_PERIOD` which will cause the failure
    params.first = round_down(params.first, TMPL_PERIOD) + _first_round
    params.last = params.first + TMPL_DURATION

    with TxnElemsContext():
        txn = payment_transaction(sender=owner, receiver=user1, amount=_amount, lease=_lease, params=params)

    with pytest.raises(algosdk.error.AlgodHTTPError, match=r'transaction .* invalid : transaction .* rejected by logic'):
        smart_signature_transaction(smart_signature, txn)
