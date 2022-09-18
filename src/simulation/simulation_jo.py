from multiprocessing.dummy import Array
from simulation_tools import Account, FreeFlowKey
from algosdk.v2client.algod import AlgodClient
import os

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

client = AlgodClient(algod_token, algod_address)

faucet = {"address": "",
          "private_key": ""}

# * create ff token capabilities

# transactions and send payments with algorand. We might want an internal Threefold
# liquidity pool for this process.

# creates funded accounts used in this simulation

def genesis(client, faucet) -> Array[Account, Account, Account, FreeFlowKey]:

    #pseudo: if files don't exist:
    if os.path.exists("free_flow_key.json"):
        from_dict = False
    else:
        from_dict = True

    alice = Account(from_dict, name="Alice", client=client, faucet=faucet)
    bob = Account(from_dict, name="Bob", client=client, faucet=faucet)
    dao = Account(from_dict, name="FreeFlow DAO", client=client, faucet=faucet)

    # creates a FreeFlowKey with the DAO as the owner
    ff_key = FreeFlowKey(from_dict,
                        asa_creator_address=dao.address,
                        asa_creator_pk=dao.private_key,
                        client=client,
                        unit_name="FreeFlowKey",
                        asset_name="FFK",
                        DAO_address=dao.private_key)
    
    # TODO: Create the faucet account and manually fill it with algorand faucet
    # Yes, that works

    alice.store()
    bob.store()
    dao.store()
    ff_key.store()

    return (alice, bob, dao, ff_key)

# Display keys that are available to be rented.
def get_rentals() -> List[Asset]:
    # TODO: get keys id's which are available to rent from algorand bc 
    # assets that 
    # requires Python SDK version 1.3 or higher
    from algosdk.v2client import indexer

    # instantiate indexer client
    myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")
    
    
    rental_keys = []
    return rental_keys

def main():

    alice, bob, dao, ff_token, ff_key = genesis() # This calling of genesis doesnt work
    # we need to perform genesis only once and in two steps, unless we figure out how
    # to access the main algorand faucet API
    # Instead, these values should be accessed from a csv file.
    print("Created accounts:\n", alice, bob, dao)
    print("Created assets:\n", ff_token, ff_key)

    alice.buy(ff_key, dao, 50_000)
    print("Alice buys key from DAO:\n")
    print(alice, bob)

    # TODO: implement the get_wallet method
    # This is just a function to get all of Alice's assets
    alice_wallet = alice.get_wallet()
    # Alice choses which key to rent out by indexing
    alice_key = alice_wallet["keys"][0]
    # TODO: Find out what unit the duration is in ie seconds/hours/days?
    alice.set_rental(alice_key, alice, 20_000, 86_400)
    print("Alice sets key up for rental:\n", alice_key)

    # separate the different functions so that we can test what happens if they 
    # set different prices for renting or disagree over other parameters
    keys_for_rent = get_rentals()
    key_to_rent = keys_for_rent[0]
    bob.rent(key_to_rent, alice, 20_000)
    print("Bob rents Alice's key:\n", key_to_rent, alice, bob)
