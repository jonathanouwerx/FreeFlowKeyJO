from src.blockchain_utils.transaction_repository import ASATransactionRepository
from src.services import NetworkInteraction, NFTRenting

# Alice's journey renting out key to Bob
# 
# 1) Alice has 100 tokens, Bob has 10 Tokens, DAO has 1 key
# 2) Alice buys a key from DAO
# 3) Alice sets key up for rental
# 4) Bob rents key for a month
# 5) Key is returned to Alice at the end of the month

# I have just allowed for nfts to be created, tokens are kind of extra and require duplication/unnecesary steps
class Asset():
    # init should do the following:
    # create asa
    # create renting object
    # modify asa to have correct management addresses
    # initialise escrow
    # fund escrow
    def __init__(self,
                 asa_creator_address: str,
                 asa_creator_pk: str,
                 client,
                 unit_name: str,
                 asset_name: str,
                 DAO_address: str,
                 asa_url=None):

        self.asa_creator_address = asa_creator_address
        self.asa_creator_pk = asa_creator_pk
        self.client = client
        self.DAO_address = DAO_address

        self.unit_name = unit_name
        self.asset_name = asset_name
        self.asa_url = asa_url
    
        # creates and signs a transaction to create an asa with total of 1 and decimals of 0
        signed_txn = ASATransactionRepository.create_asa(
            client=self.client,
            creator_private_key=self.asa_creator_pk,
            unit_name=self.unit_name,
            asset_name=self.asset_name,
            total=1,
            decimals=0,
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

        # create renting application
        # admin below is simply the creating user, as they are admin in initial phases
        nft_renting_tool = NFTRenting(admin_pk=self.asa_creator_pk,
                                      admin_address=self.asa_creator_address,
                                      nft_id=self.asa_id,
                                      DAO_address = self.DAO_address,
                                      NFT_owner_address = self.asa_creator_address,
                                      client=client)

        nft_renting_tool.app_initialization(nft_owner_address=self.asa_creator_address)

        # change freeze/clawback addresses of the nft to escrow  
        # change manager address to DAO
        # change reserve address to ''
        modify_asa_txn = ASATransactionRepository.change_asa_management(
            client=self.client,
            current_manager_pk=self.nft_creator_pk,
            asa_id=self.nft_id,
            manager_address=self.DAO_address,
            reserve_address="",
            freeze_address=nft_renting_tool.escrow_address,
            strict_empty_address_check=False,
            clawback_address=nft_renting_tool.escrow_address,
            sign_transaction=True,
        )

        NetworkInteraction.submit_transaction(self.client, transaction=modify_asa_txn)
        
        # initialise escrow
        nft_renting_tool.intialise_escrow()

        # fund escrow 
        ### the funding amount is currently way too high and needs to be reduced
        nft_renting_tool.fund_escrow()



    def __repr__():
        # TODO: get asset info on algorand bc
        asset_info = get_assets()
        return(self.asset_name + ": " + asset_info)



class asaService:
    def __init__(
            self,
            asa_creator_address: str,
            asa_creator_pk: str,
            client,
            unit_name: str,
            asset_name: str,
            asa_url=None,
    ):
        self.asa_creator_address = asa_creator_address
        self.asa_creator_pk = asa_creator_pk
        self.client = client

        self.unit_name = unit_name
        self.asset_name = asset_name
        self.asa_url = asa_url

        self.asa_id = None

    def create_asa(self):
        signed_txn = ASATransactionRepository.create_non_fungible_asa(
            client=self.client,
            creator_private_key=self.asa_creator_pk,
            unit_name=self.unit_name,
            asset_name=self.asset_name,
            note=None,
            manager_address=self.asa_creator_address,
            reserve_address=self.asa_creator_address,
            freeze_address=self.asa_creator_address,
            clawback_address=self.asa_creator_address,
            url=self.asa_url,
            default_frozen=True,
            sign_transaction=True,
        )

        asa_id, tx_id = NetworkInteraction.submit_asa_creation(
            client=self.client, transaction=signed_txn
        )
        self.asa_id = asa_id
        return tx_id

    def change_asa_credentials_txn(self, escrow_address):
        txn = ASATransactionRepository.change_asa_management(
            client=self.client,
            current_manager_pk=self.asa_creator_pk,
            asa_id=self.asa_id,
            manager_address="",
            reserve_address="",
            freeze_address="",
            strict_empty_address_check=False,
            clawback_address=escrow_address,
            sign_transaction=True,
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=txn)

        return tx_id

    def opt_in(self, account_pk):
        opt_in_txn = ASATransactionRepository.asa_opt_in(
            client=self.client, sender_private_key=account_pk, asa_id=self.asa_id
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=opt_in_txn)
        return tx_id







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


