import json
from src.services.nft_manager import NFTManager
from src.services.network_interaction import NetworkInteraction

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
            print(f"Initializing FreeFlowKey instance...")

            client = kwargs.get('client', None)

            self.asa_creator_address = kwargs.get('asa_creator_address', None)
            self.asa_creator_pk = kwargs.get('asa_creator_pk', None)
            
            self.DAO_address = kwargs.get('DAO_address', None) # RHS 4 # LHS 5

            self.unit_name = kwargs.get('unit_name', None)
            self.asset_name = kwargs.get('asset_name', None)
            self.asa_url = kwargs.get('asa_url', None)
            
            # creates and signs a transaction to create an asa with total of 1 and decimals of 0
            signed_txn = ASATransactionRepository.create_asa(
                client=client,
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
                default_frozen=False,
                sign_transaction=True,
            )

            # submits asa creation transaction and receices the transaction id and asa id
            asa_id, txid = NetworkInteraction.submit_asa_creation(
                client=client, transaction=signed_txn
            )

            print(" - Asset created successfully")

            self.asa_id = asa_id

            # create management application
            # admin below is simply the creating user, as they are admin in initial phases
            nft_manager_tool = NFTManager(admin_pk=self.asa_creator_pk,
                                        admin_address=self.asa_creator_address,
                                        nft_id=self.asa_id, # LHS 3
                                        DAO_address = self.DAO_address, # RHS 3
                                        NFT_owner_address = self.asa_creator_address,
                                        client=client)

            self.nft_manager_tool = nft_manager_tool

            self.nft_manager_tool.app_initialization()

            print(" - Stateful contract initialized successfully.")

            # change freeze/clawback addresses of the nft to escrow  
            # change manager address to DAO
            # change reserve address to ''

            modify_asa_txn = ASATransactionRepository.change_asa_management(
                client=client,
                current_manager_pk=self.asa_creator_pk,
                asa_id=self.asa_id, 
                manager_address=self.DAO_address, # LHS 4
                reserve_address="",
                freeze_address=self.nft_manager_tool.escrow_address,
                strict_empty_address_check=False,
                clawback_address=self.nft_manager_tool.escrow_address,
                sign_transaction=True,
            )

            NetworkInteraction.submit_transaction(client, transaction=modify_asa_txn)
            
            print(" - Asset modified successfully.")

            # initialise escrow
            self.nft_manager_tool.initialize_escrow()
            print(" - Stateless contract initialized successfully.")

            # fund escrow 
            # TODO: the funding amount is currently way too high and needs to be reduced
            # TODO: I should make funding amount a parameter
            # The owner will fund everything
            self.nft_manager_tool.fund_escrow()
            print(" - Stateless contract funded successfully.")

        else: 
            print(f"Retrieving instance of FreeFlowKey...")
            with open(f"src/simulation/free_flow_key.json", "r") as self_file:
                self_dict = json.load(self_file)
            print(" - json file accessed")
            for key in self_dict:
                setattr(self, key, self_dict[key])
            print(" - object created")

    def store(self):
        print(self.__dict__)
        print(json.dumps(self.__dict__))
        with open(f"src/simulation/free_flow_key.json", "w") as self_file:
            json.dump(self.__dict__, self_file)
        print(f"Instance of FreeFlowKey has been stored in a json file")

    # TODO: Discover how to get account info from algorand blockchain
    '''
    def __repr__():
        asset_info = get_assets()
        return(self.asset_name + ": " + asset_info)
    '''



class Account():
    def __init__(self, from_dict, **kwargs):
        '''
        Inputs: from_dict, name
        '''
        if from_dict == False:
            # TODO: clarify how the private key is going to be managed in this simulation
            # Do we want to keep it separate and only input it in necessary functions
            # or have it as an attribute of the Account class
            # For this simulation, we can leave private key as attribute
            self.name = kwargs.get('name', None)
            
            print(f"Creating account for {self.name}...")

            private_key, address = account.generate_account()
            self.private_key = private_key
            self.address = address
            self.mnemonic = mnemonic.from_private_key(private_key)
            print(" - account created")
            # TODO: Clarify how client should be used ie defined on init and inputted
            # as a parameter each time a function is called
            # Leave as is for now, as it is simulation
            client = kwargs.get('client', None)
            faucet = kwargs.get('faucet', None)
            # TODO: Fix the funding process
            self.fund(client, faucet, 500_000)
            #self.wallet: Dict[Asset, int] = {: amount, tokens: []}
            
            print(" - account funded")

        else: 
            print(f"Retrieving account for {kwargs.get('name', None)}...")
            with open(f"src/simulation/{kwargs.get('name', None)}.json", "r") as self_file:
                self_dict = json.load(self_file)
            print(" - json file accessed")
            for key in self_dict:
                setattr(self, key, self_dict[key])
            print(" - object created")
    
    def store(self):
        with open(f"src/simulation/{self.name}.json", "w") as self_file:
            json.dump(self.__dict__, self_file)
        print(f"{self.name}'s account has been stored in a json file")

    # TODO: Discover how to get account info from algorand blockchain
    '''
    def __repr__():
        asset_info = ""
        return(self.name + ": " + asset_info)
    '''
    
    def get_wallet(self):
        pass
        # TODO: get all assets associated to account

    # client needs to be added up a tier
    def fund(self, client, faucet: dict, amount: int):
        txn_id = PaymentTransactionRepository.payment(client=client,
                                                    sender_address=faucet["address"],
                                                    receiver_address=self.address,
                                                    amount=amount,
                                                    sender_private_key=faucet["private_key"],
                                                    sign_transaction=True)

    @property
    def optin(self, client, asset: FreeFlowKey):
        opt_in_txn = ASATransactionRepository.asa_opt_in(
            client=client, sender_private_key=self.pk, asa_id=asset.asa_id
        )

        tx_id = NetworkInteraction.submit_transaction(client, transaction=opt_in_txn)

    #def buy(self, asset: FreeFlowKey, seller: Account, amount: int):
    def buy(self, client, asset, seller, amount):
        self.optin(client, asset)
        self.nft_manager_tool.buy_nft(self.address, self.pk, seller.pk, amount)

    def set_rental(self, asset: FreeFlowKey, amount: int, duration: int):
        # TODO: One thing to test is whether you can opt-in to an asset multiple times
        asset.nft_manager_tool.make_rent_offer(amount, duration, self.pk)

    def rent(self, client, asset: FreeFlowKey, amount: int):
        self.optin(client, asset)
        asset.nft_manager_tool.rent_nft(self.address, self.pk, amount)