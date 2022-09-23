from multiprocessing.dummy import Array
import os
import sys 

sys.path.append(os.path.abspath("/Users/Jonathan/code/github/algorand/FreeFlowKeyJO"))
from src.simulation.simulation_tools import Account, FreeFlowKey



# * create ff token capabilities
        
# transactions and send payments with algorand. We might want an internal Threefold
# liquidity pool for this process.

# creates funded accounts used in this simulation
#def genesis(client, faucet) -> Array[Account, Account, Account, FreeFlowKey]:
def genesis(client, faucet):

    def generate(name):
        from_dict = os.path.exists(f"src/simulation/{name}.json")
        account = Account(from_dict, name=name, client=client, faucet=faucet)
        account.store()
        print("")
        return account
        
    alice = generate("Alice")
    bob = generate("Bob")
    dao = generate("FreeFlowDAO")

    ffk_dict = os.path.exists("src/simulation/free_flow_key.json")

    # creates a FreeFlowKey with the DAO as the owner
    ff_key = FreeFlowKey(ffk_dict,
                        asa_creator_address=dao.address,
                        asa_creator_pk=dao.private_key,
                        client=client,
                        unit_name="FFK",
                        asset_name="FreeFlowKey",
                        DAO_address=dao.address)
    
    ff_key.store()

    return (alice, bob, dao, ff_key)

# Display keys that are available to be rented.
# def get_rentals() -> List[Asset]:
def get_rentals():
    # TODO: get keys id's which are available to rent from algorand bc 
    # assets that 
    # requires Python SDK version 1.3 or higher
    from algosdk.v2client import indexer

    # instantiate indexer client
    myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")
    
    
    rental_keys = []
    return rental_keys

def main(client, faucet):

    alice, bob, dao, ff_key = genesis(client, faucet) # This calling of genesis doesnt work
    # we need to perform genesis only once and in two steps, unless we figure out how
    # to access the main algorand faucet API
    # Instead, these values should be accessed from a csv file.
    print("Created accounts:\n", alice,"\n",bob,"\n", dao)
    print("Created asset:\n", ff_key)

    exit()

    alice.buy(client, ff_key, dao, 50_000)
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
    bob.rent(client, key_to_rent, alice, 20_000)
    print("Bob rents Alice's key:\n", key_to_rent, alice, bob)
