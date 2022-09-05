# Alice's journey renting out key to Bob
# 
# 1) Alice has 100 tokens, Bob has 10 Tokens, DAO has 1 key
# 2) Alice buys a key from DAO
# 3) Alice sets key up for rental
# 4) Bob rents key for a month
# 5) Key is returned to Alice at the end of the month

class Asset():
    def __init__(name: str, fungible: bool):
        self.name = name

        # TODO: create algorand assets
        if fungible:
            # create token
        else:
            # create nft             

    def __repr__():
        # TODO: get asset info on algorand bc
        asset_info = get_assets()
        return(self.name + ": " + asset_info)


class Account():
    def __init__(name: str):
        self.name = name
        self.wallet: Dict[Asset, int] = {: amount, tokens: []}
        # TODO: create algorand account

    def __repr__():
        # TODO: get account info on algorand bc
        asset_info = ""
        return(self.name + ": " + asset_info)
        
    def fund(asset: Asset, amount: int):
        # TODO: fund algorand wallet
        asset_ids = []
        self.wallet

    def buy(seller: Account, asset: Asset, amount: int):
        # TODO: perform tx

    def rent(renter: Account, asset: Asset, duration: int):
        # TODO: perform tx


