import json
from src.services import NetworkInteraction, NFTManager
from algosdk import account, mnemonic
from src.blockchain_utils.transaction_repository import (
    ApplicationTransactionRepository,
    ASATransactionRepository,
    PaymentTransactionRepository,
)


# Alice's journey renting out key to Bob
# 
# 1) Alice has 100 tokens, Bob has 10 Tokens, DAO has 1 key
# 2) Alice buys a key from DAO
# 3) Alice sets key up for rental
# 4) Bob rents key for a month
# 5) Key is returned to Alice at the end of the month


# I have just allowed for nfts to be created, tokens are kind of extra and require duplication/unnecesary steps
class FreeFlowKey():
    # init should do the following:
    # create asa
    # create renting object
    # modify asa to have correct management addresses
    # initialise escrow
    # fund escrow
    def __init__(self, from_dict, **kwargs):
        if from_dict == False:
            
            self.asa_creator_address = kwargs.get('asa_creator_address', None)
            self.asa_creator_pk = kwargs.get('asa_creator_pk', None)
            self.client = kwargs.get('client', None)
            self.DAO_address = kwargs.get('DAO_address', None)

            self.unit_name = kwargs.get('unit_name', None)
            self.asset_name = kwargs.get('asset_name', None)
            self.asa_url = kwargs.get('asa_url', None)
        
            # creates and signs a transaction to create an asa with total of 1 and decimals of 0
            signed_txn = ASATransactionRepository.create_asa(
                client=self.client,
                creator_private_key=self.asa_creator_pk,
                unit_name=self.unit_name,
                asset_name=self.asset_name,
                total=1,
                decimals=0, ### This needs to be decided
                note=None,
                manager_address=self.asa_creator_address,
                reserve_address=self.asa_creator_address,
                freeze_address=self.asa_creator_address,
                clawback_address=self.asa_creator_address,
                url=self.asa_url,
                default_frozen=True,
                sign_transaction=True,
            )

            # submits asa creation transaction and receices the transaction id and asa id
            asa_id = NetworkInteraction.submit_asa_creation(
                client=self.client, transaction=signed_txn
            )

            self.asa_id = asa_id

            # create management application
            # admin below is simply the creating user, as they are admin in initial phases
            nft_manager_tool = NFTManager(admin_pk=self.asa_creator_pk,
                                        admin_address=self.asa_creator_address,
                                        nft_id=self.asa_id,
                                        DAO_address = self.DAO_address,
                                        NFT_owner_address = self.asa_creator_address,
                                        client=client)

            self.nft_manager_tool = nft_manager_tool

            self.nft_manager_tool.app_initialization(nft_owner_address=self.asa_creator_address)

            # change freeze/clawback addresses of the nft to escrow  
            # change manager address to DAO
            # change reserve address to ''
            modify_asa_txn = ASATransactionRepository.change_asa_management(
                client=self.client,
                current_manager_pk=self.nft_creator_pk,
                asa_id=self.nft_id,
                manager_address=self.DAO_address,
                reserve_address="",
                freeze_address=self.nft_manager_tool.escrow_address,
                strict_empty_address_check=False,
                clawback_address=self.nft_manager_tool.escrow_address,
                sign_transaction=True,
            )

            NetworkInteraction.submit_transaction(self.client, transaction=modify_asa_txn)
            
            # initialise escrow
            self.nft_manager_tool.intialise_escrow()

            # fund escrow 
            # TODO: the funding amount is currently way too high and needs to be reduced
            # TODO: I should make funding amount a parameter
            # The owner will fund everything
            self.nft_manager_tool.fund_escrow()
        else: 
            with open(f"simulation/free_flow_key.json", "w") as self_file:
                self_dict = json.load(self_file)
            for key in self_dict:
                setattr(self, key, self_dict[key])

    def store(self):
        with open(f"simulation/free_flow_key.json", "w") as self_file:
            json.dump(self.__dict__, self_file)

    # TODO: Discover how to get account info from algorand blockchain
    '''
    def __repr__():
        asset_info = get_assets()
        return(self.asset_name + ": " + asset_info)
    '''



class Account():
    def __init__(self, from_dict, **kwargs):
        '''
        Inputs: from_dict, name, client
        '''
        if from_dict == False:
            # TODO: clarify how the private key is going to be managed in this simulation
            # Do we want to keep it separate and only input it in necessary functions
            # or have it as an attribute of the Account class
            # For this simulation, we can leave private key as attribute
            self.name = kwargs.get('name', None)
            
            private_key, address = account.generate_account()
            self.private_key = private_key
            self.address = address
            self.mnemonic = mnemonic.from_private_key(private_key)
            # TODO: Clarify how client should be used ie defined on init and inputted
            # as a parameter each time a function is called
            # Leave as is for now, as it is simulation
            self.client = kwargs.get('client', None)
            
            faucet = kwargs.get('faucet', None)
            self.fund(faucet, 500_000)
            #self.wallet: Dict[Asset, int] = {: amount, tokens: []}
        else: 
            with open(f"simulation/{kwargs.get('name', None)}.json", "w") as self_file:
                self_dict = json.load(self_file)
            for key in self_dict:
                setattr(self, key, self_dict[key])
    
    def store(self):
        with open(f"simulation/{self.name}.json", "w") as self_file:
            json.dump(self.__dict__, self_file)

    # TODO: Discover how to get account info from algorand blockchain
    '''
    def __repr__():
        asset_info = ""
        return(self.name + ": " + asset_info)
    '''
    
    def get_wallet(self):
        pass
        # TODO: get all assets associated to account

    def fund(self, faucet: dict, amount: int):
        txn_id = PaymentTransactionRepository.payment(client=self.client,
                                                    sender_address=faucet["address"],
                                                    receiver_address=self.address,
                                                    amount=amount,
                                                    sender_private_key=faucet["private_key"],
                                                    sign_transaction=True)

    @property
    def optin(self, asset: Asset):
        opt_in_txn = ASATransactionRepository.asa_opt_in(
            client=self.client, sender_private_key=self.pk, asa_id=asset.asa_id
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=opt_in_txn)

    def buy(self, asset: Asset, seller: Account, amount: int):
        self.optin(asset)
        self.nft_manager_tool.buy_nft(self.address, self.pk, seller.pk, amount)

    def set_rental(self, asset: Asset, amount: int, duration: int):
        # TODO: One thing to test is whether you can opt-in to an asset multiple times
        asset.nft_manager_tool.make_rent_offer(amount, duration, self.pk)

    def rent(self, asset: Asset, amount: int):
        self.optin(asset)
        asset.nft_manager_tool.rent_nft(self.address, self.pk, amount)