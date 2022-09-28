import sys

from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk import encoding

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "2MOR0HMzNG92jNIN89adW6GWQn0vcNL28JhWy9zT"
headers = {"X-API-Key": algod_token}

client = algod.AlgodClient(algod_token, algod_address, headers)
dao_address = "LDPQGAISML43336YL7GAO4IEHJGGT7KTWJ3KTK5J52Q5B5WHZURKUEQU2M"

suggested_params = client.suggested_params()
suggested_params.flat_fee = True
suggested_params.fee = 1000

txn = transaction.AssetConfigTxn(sender=dao_address,
                                sp=suggested_params,
                                total=1,
                                default_frozen=False,
                                unit_name="FFK",
                                asset_name="FreeFlowKey",
                                manager=dao_address,
                                reserve=dao_address,
                                freeze=dao_address,
                                clawback=dao_address,
                                url="https://threefold.io/",
                                decimals=3,
                                note="FreeFlowKey Creation")

encoded_unsigned = encoding.msgpack_encode(txn)
message = "FreeFlowKey Created"
signer = dao_address

wallet_transaction = [encoded_unsigned, message, signer]

sys.stdout.write(wallet_transaction)
