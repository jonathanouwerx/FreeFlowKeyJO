import Account, Asset

# creates funded accounts used in this simulation
def genesis() -> Tuple[Account, Account, Account, Asset, Asset]:
    ff_token = Asset("FreeFlow Token", True)
    ff_key = Asset("FreeFlow Key", False)

    alice = Account("Alice")
    bob = Account("Bob")
    dao = Account("FreeFlow DAO")

    alice.fund(ff_token, 100)
    bob.fund(ff_token, 10)
    dao.fund(ff_key, 1)

    return (alice, bob, dao, ff_token, ff_key)

def get_rentals() -> List[Asset]:
    # TODO: get rental keys id's from algorand bc 
    rental_keys = []
    return rental_keys

def main():
    alice, bob, dao, ff_token, ff_key = genesis()
    print("Created accounts:\n", alice, bob, dao)
    print("Created assets:\n", ff_token, ff_key)

    keys = (1, ff_key)
    price = (100, ff_token)
    alice.buy(keys, price, dao)
    print("Alice buys key from DAO:\n")
    print(alice, bob)

    alice_wallet = Alice.get_wallet()
    alice_key = alice_wallet["keys"][0]
    rent_fee = (10, ff_token)
    alice.set_rental(alice_key, rent_fee)
    print("Alice sets key up for rental:\n", alice_key)

    key = get_rentals()[0]
    rent_fee = (10, ff_token)
    bob.rent(key, rent_fee)
    print("Bob rents Alice's key:\n", key, alice, bob)

