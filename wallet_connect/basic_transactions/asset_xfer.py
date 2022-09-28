import sys
# first argument is the payment_sender address
payment_sender = sys.argv[1]

# second argument is the amount
amount = sys.argv[2]

# third argument is the asset_sender address
asset_sender = sys.argv[3]

# fourth argument is the asa_id
asa_id = sys.argv[4]


from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import encoding

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "2MOR0HMzNG92jNIN89adW6GWQn0vcNL28JhWy9zT"
headers = {"X-API-Key": algod_token}

client = algod.AlgodClient(algod_token, algod_address, headers)

suggested_params = client.suggested_params()

payment_txn = transaction.PaymentTxn(sender=payment_sender,
                                        sp=suggested_params,
                                        receiver=asset_sender,
                                        amt=amount)

xfer_txn = transaction.AssetTransferTxn(sender=asset_sender,
                                            sp=suggested_params,
                                            receiver=payment_sender,
                                            amt=amount,
                                            index=asa_id)

gid = transaction.calculate_group_id([payment_txn, xfer_txn])
payment_txn.group = gid
xfer_txn.group = gid

def stdout_encoded(txn, message, signer):
    wallet_transaction_payment = [txn, message, signer]
    sys.stdout.write(wallet_transaction_payment)  

encoded_payment_txn = encoding.msgpack_encode(payment_txn)
payment_message = f"Send {amount} microAlgos to {receiver_address}. Receive asset with ID: {asa_id}"
stdout_encoded(encoded_payment_txn, payment_message, payment_sender)

encoded_xfer_txn = encoding.msgpack_encode(xfer_txn)
xfer_message = f"Receive {amount} microAlgos from {sender_address}. Send asset with ID: {asa_id}"
stdout_encoded(encoded_xfer_txn, payment_message, asset_sender)



