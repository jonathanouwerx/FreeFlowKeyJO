import sys
# first argument is the sender_address
sender_address = sys.argv[1]

# second argument is the receiver_address
receiver_address = sys.argv[2]

# third argument is the amount
amount = sys.argv[3]

from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import encoding

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "2MOR0HMzNG92jNIN89adW6GWQn0vcNL28JhWy9zT"
headers = {"X-API-Key": algod_token}

client = algod.AlgodClient(algod_token, algod_address, headers)

suggested_params = client.suggested_params()

txn = transaction.PaymentTxn(sender=sender_address,
                        sp=suggested_params,
                        receiver=receiver_address,
                        amt=amount)

encoded_unsigned = encoding.msgpack_encode(txn)
message = f"Send {amount} microAlgos to {receiver_address}"
message = "FreeFlowKey Created"
signer = sender_address

wallet_transaction = [encoded_unsigned, message, signer]

sys.stdout.write(wallet_transaction)
