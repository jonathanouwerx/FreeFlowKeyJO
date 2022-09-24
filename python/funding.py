from src.blockchain_utils.transaction_repository import PaymentTransactionRepository
from algosdk.v2client.algod import AlgodClient

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

client = AlgodClient(algod_token, algod_address) #, headers)

txn_id = PaymentTransactionRepository.payment(client=client,
                                            sender_address='NIVDZGJME6NZ2XCMZ3RMHGRSWSE3U2E3PUXMOYDXTN2A75D5Y5EH6U66BQ',
                                            receiver_address='OUTRUUXQS4H5C37DSOZ4ESYTJZW2S4VAREWPDH6OYLCHUORIZIL7IOTKBY',
                                            amount=1_000_000,
                                            sender_private_key='NIVDZGJME6NZ2XCMZ3RMHGRSWSE3U2E3PUXMOYDXTN2A75D5Y5EH6U66BQ',
                                            sign_transaction=True)



