# This example is provided for informational purposes only and has not been audited for security.
import base64
from pyteal import *

tmpl_fee = Int(1000)
tmpl_period = Int(50)
tmpl_amount = Int(2_000_000)
tmpl_duration = Int(50)
tmpl_lease = "fillerfillerfillerfillerfiller"

# The lease in the smart signature is actually the base64 encoding of whatever
# was input into the transaction `lease` parameter
def format_lease(lease_str):
    return Bytes("base64", base64.b64encode(lease_str.encode()).decode())

def recurring_txns(receivers_addr):
    num_txns_cond = Global.group_size() == Int(len(receivers_addr))
    txn_conds = []

    for i, receiver_addr in enumerate(receivers_addr):
        txn_unit = Gtxn[i]
            
        tx_type_cond = txn_unit.type_enum() == TxnType.Payment        
        fee_cond = txn_unit.fee() <= tmpl_fee
        recv_cond = txn_unit.receiver() == Addr(receiver_addr)
        amount_cond = txn_unit.amount() == tmpl_amount
        
        # Combine together all of the parameter conditions
        params_conds = And(num_txns_cond, tx_type_cond, fee_cond, recv_cond, amount_cond)
        
        first_valid_cond = txn_unit.first_valid() % tmpl_period == Int(0)
        last_valid_cond = txn_unit.last_valid() == tmpl_duration + txn_unit.first_valid()
        lease_cond = txn_unit.lease() == format_lease(f'{tmpl_lease}_{i}')

        # Combine together all of the recurring conditions
        recurring_conds = And(first_valid_cond, last_valid_cond, lease_cond)
        
        close_remainder_cond = txn_unit.close_remainder_to() == Global.zero_address()
        rekey_cond = txn_unit.rekey_to() == Global.zero_address()
        
        # Combine the safety conditions
        safety_conds = And(close_remainder_cond, rekey_cond)

        # Append the conditions for this transaction in the group
        txn_conds.append(And(params_conds, recurring_conds, safety_conds))

    # Generate one big `And` condition for all of the transactions in the group
    return And(num_txns_cond, *txn_conds)


if __name__ == "__main__":
    receiver = "B6Q6ZZOH5IOCG5PJ366WJU26L5Y2EASQK6ZIC7K6H3V62PZTG7HOW4FKAA"
    print(compileTeal(recurring_txns([receiver]), mode=Mode.Signature, version=5))
