from src.simulation.simulation_jo import main, genesis
from algosdk.v2client.algod import AlgodClient
from algosdk import account, mnemonic

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "2MOR0HMzNG92jNIN89adW6GWQn0vcNL28JhWy9zT"
headers = {"X-API-Key": algod_token}

#algod_address = "http://localhost:4001"
#algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

client = AlgodClient(algod_token, algod_address, headers)

faucet = {"address": "4DIMPSW5MJ64G56KO7FW3AYA7PH5KCUYNF4LKY4KVAHB6MHYSKDNJVMG7Y",
        "private_key": "upLrumxBj3rCe54JegZW2m3795fQ/WZIOdGqvQX71jPg0MfK3WJ9w3fKd8ttgwD7z9UKmGl4tWOKqA4fMPiShg=="}

main(client, faucet)

