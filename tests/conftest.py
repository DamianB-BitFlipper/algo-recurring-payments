from pyteal import Mode
from algopytest import compile_program
from pytest import fixture
from algosdk.transaction import LogicSigAccount

# Load the smart signatures from this project. The path to find these
# imports is set by the environment variable `$PYTHONPATH`.
from recurring_payments_smart_sig import recurring_txns


@fixture
def smart_signature(owner, user1):
    """Generate a smart signature where ``user1`` may periodically pull from ``owner``."""
    compiled_program = compile_program(recurring_txns([user1.address]), mode=Mode.Signature)
    lsig = LogicSigAccount(compiled_program)
    lsig.sign(owner.private_key)
    return lsig

@fixture
def smart_signature_two_receivers(owner, user1, user2):
    """Generate a smart signature where both ``user1`` and ``user2`` may periodically pull from ``owner``."""    
    compiled_program = compile_program(recurring_txns([user1.address, user2.address]), mode=Mode.Signature)
    lsig = LogicSigAccount(compiled_program)
    lsig.sign(owner.private_key)
    return lsig
