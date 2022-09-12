from multiprocessing.dummy import Array
from simulation import Account, FreeFlowKey
from algosdk.v2client.algod import AlgodClient

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

client = AlgodClient(algod_token, algod_address)



### TODO: resolve transaction currency issue. We have to use algos to fund
# transactions and send payments with algorand. We might want an internal Threefold
# liquidity pool for this process.

# creates funded accounts used in this simulation
def genesis(client, faucet) -> Array[Account, Account, Account, FreeFlowKey]:

    # also we dont want to do create new accounts every time, so we should store in a file
    # TODO: Account init method
    alice = Account("Alice")
    bob = Account("Bob")
    dao = Account("FreeFlow DAO")

    # creates a FreeFlowKey with the DAO as the owner
    ff_key = FreeFlowKey((dao.address,
                          dao.pk,
                          client,
                          "FreeFlowKey1",
                          "FFK",
                          dao.pk,
                          None))

    # TODO: Create the faucet account and manually fill it with algorand faucet
    alice.fund(faucet, 500_000)
    bob.fund(faucet, 500_000)
    dao.fund(faucet, 500_000)

    return (alice, bob, dao, ff_key)

def get_rentals() -> List[Asset]:
    # TODO: get rental keys id's from algorand bc 
    rental_keys = []
    return rental_keys

def main():
    alice, bob, dao, ff_token, ff_key = genesis() # This calling of genesis doesnt work
    # we need to perform genesis only once and in two steps, unless we figure out how
    # to access the main algorand faucet API
    # Instead, these values should be accessed from a csv file.
    print("Created accounts:\n", alice, bob, dao)
    print("Created assets:\n", ff_token, ff_key)

    #keys = (1, ff_key)
    #price = (100, ff_token)
    alice.buy(ff_key, dao, 50_000)
    print("Alice buys key from DAO:\n")
    #print(alice, bob)

    # TODO: implement the get_wallet method
    alice_wallet = Alice.get_wallet()
    alice_key = alice_wallet["keys"][0]
    rent_fee = (10, ff_token)
    alice.set_rental(alice_key, rent_fee)
    print("Alice sets key up for rental:\n", alice_key)

    key = get_rentals()[0]
    rent_fee = (10, ff_token)
    bob.rent(key, rent_fee)
    print("Bob rents Alice's key:\n", key, alice, bob)

