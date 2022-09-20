from src.simulation.simulation_jo import main, genesis
from algosdk.v2client.algod import AlgodClient
from algosdk import account, mnemonic

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

client = AlgodClient(algod_token, algod_address)

faucet = {"address": "4DIMPSW5MJ64G56KO7FW3AYA7PH5KCUYNF4LKY4KVAHB6MHYSKDNJVMG7Y",
        "private_key": "upLrumxBj3rCe54JegZW2m3795fQ/WZIOdGqvQX71jPg0MfK3WJ9w3fKd8ttgwD7z9UKmGl4tWOKqA4fMPiShg=="}

main(client, faucet)

quit()

from src.blockchain_utils.transaction_repository import ASATransactionRepository
from src.services.network_interaction import NetworkInteraction
from algosdk.future import transaction as algo_txn

signed_txn = ASATransactionRepository.create_asa(
                client=client,
                creator_private_key=faucet["private_key"],
                unit_name= "FFK",
                asset_name= "FreeFlowKey",
                total=1,
                decimals=0, ### This needs to be decided
                note=None,
                manager_address=faucet["address"],
                reserve_address=faucet["address"],
                freeze_address=faucet["address"],
                clawback_address=faucet["address"],
                url=None,
                default_frozen=True,
                sign_transaction=True,
            )


suggested_params = client.suggested_params()

print(suggested_params)

txn = algo_txn.AssetConfigTxn(sender=faucet["address"],
                                sp=suggested_params,
                                total=1,
                                default_frozen=False,
                                unit_name="FFK",
                                asset_name="FreeFlowKey",
                                manager=faucet["address"],
                                reserve=faucet["address"],
                                freeze=faucet["address"],
                                clawback=faucet["address"],
                                decimals=0)

print("\nTransaction created successfully\n")

signed_txn = txn.sign(private_key=faucet["private_key"])

print("\nTransaction signed successfully\n")

txid = client.send_transaction(signed_txn)

print("\nTransaction sent successfully\n")

NetworkInteraction.wait_for_confirmation(client, txid)

print("\nWaiting for confirmation...\n")

try:
        ptx = client.pending_transaction_info(txid)
        print("Asset ID and Transaction ID:")
        print(ptx["asset-index"], txid)
except Exception as e:
        # TODO: Proper logging needed.
        print(e)
        print('Unsuccessful creation of Algorand Standard Asset.')


print("\nTransaction submitted successfully\n")

