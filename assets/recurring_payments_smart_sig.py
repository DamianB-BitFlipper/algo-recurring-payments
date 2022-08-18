# This example is provided for informational purposes only and has not been audited for security.
import base64
from pyteal import *

tmpl_fee = Int(1000)
tmpl_period = Int(50)
tmpl_amount = Int(2_000_000)
tmpl_duration = Int(50)

# The lease in the smart signature is actually the base64 encoding of whatever
# was input into the transaction `lease` parameter
tmpl_lease = Bytes("base64", base64.b64encode('passwordpasswordpasswordpassword'.encode()).decode())


def recurring_txns(receiver_addr_str):
    receiver_addr = Addr(receiver_addr_str)

    def program():
        tx_type_cond = Txn.type_enum() == TxnType.Payment        
        fee_cond = Txn.fee() <= tmpl_fee
        recv_cond = Txn.receiver() == receiver_addr        
        amount_cond = Txn.amount() == tmpl_amount
        
        # Combine together all of the parameter conditions
        params_conds = And(tx_type_cond, fee_cond, recv_cond, amount_cond)
        
        first_valid_cond = Txn.first_valid() % tmpl_period == Int(0)
        last_valid_cond = Txn.last_valid() == tmpl_duration + Txn.first_valid()
        lease_cond = Txn.lease() == tmpl_lease

        # Combine together all of the recurring conditions
        recurring_conds = And(first_valid_cond, last_valid_cond, lease_cond)
        
        close_remainder_cond = Txn.close_remainder_to() == Global.zero_address()
        rekey_cond = Txn.rekey_to() == Global.zero_address()
        
        # Combine the safety conditions
        safety_conds = And(close_remainder_cond, rekey_cond)
        return And(params_conds, recurring_conds, safety_conds)

    return program


if __name__ == "__main__":
    receiver = "B6Q6ZZOH5IOCG5PJ366WJU26L5Y2EASQK6ZIC7K6H3V62PZTG7HOW4FKAA"
    print(compileTeal(recurring_txns(receiver), mode=Mode.Signature, version=5))
