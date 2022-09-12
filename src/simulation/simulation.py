from src.services import NetworkInteraction, NFTRenting
from algosdk import account, mnemonic
from src.blockchain_utils.transaction_repository import (
    ApplicationTransactionRepository,
    ASATransactionRepository,
    PaymentTransactionRepository,
)
from algosdk.future import transaction

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

        # create renting application
        # admin below is simply the creating user, as they are admin in initial phases
        nft_renting_tool = NFTRenting(admin_pk=self.asa_creator_pk,
                                      admin_address=self.asa_creator_address,
                                      nft_id=self.asa_id,
                                      DAO_address = self.DAO_address,
                                      NFT_owner_address = self.asa_creator_address,
                                      client=client)

        self.nft_renting_tool = nft_renting_tool

        self.nft_renting_tool.app_initialization(nft_owner_address=self.asa_creator_address)

        # change freeze/clawback addresses of the nft to escrow  
        # change manager address to DAO
        # change reserve address to ''
        modify_asa_txn = ASATransactionRepository.change_asa_management(
            client=self.client,
            current_manager_pk=self.nft_creator_pk,
            asa_id=self.nft_id,
            manager_address=self.DAO_address,
            reserve_address="",
            freeze_address=self.nft_renting_tool.escrow_address,
            strict_empty_address_check=False,
            clawback_address=self.nft_renting_tool.escrow_address,
            sign_transaction=True,
        )

        NetworkInteraction.submit_transaction(self.client, transaction=modify_asa_txn)
        
        # initialise escrow
        self.nft_renting_tool.intialise_escrow()

        # fund escrow 
        # TODO: the funding amount is currently way too high and needs to be reduced
        # TODO: I should make funding amount a parameter
        self.nft_renting_tool.fund_escrow()




    def __repr__():
        # TODO: get asset info on algorand bc
        asset_info = get_assets()
        return(self.asset_name + ": " + asset_info)







class Account():
    def __init__(self, name: str, client):
        self.name = name

        private_key, address = account.generate_account()
        self.private_key = private_key
        self.address = address
        self.mnemonic = mnemonic.from_private_key(private_key)
        # TODO: Clarify how client should be used ie defined on init and inputted
        # as a parameter each time a function is called
        self.client = client
        
        #self.wallet: Dict[Asset, int] = {: amount, tokens: []}
    
    # TODO: Discover how to do this
    '''
    def __repr__():
        # TODO: get account info on algorand bc
        asset_info = ""
        return(self.name + ": " + asset_info)
    '''
        
    def fund(self, faucet: Account, amount: int):
        txn_id = PaymentTransactionRepository.payment(client=self.client,
                                                    sender_address=faucet.address,
                                                    receiver_address=self.address,
                                                    amount=amount,
                                                    sender_private_key=self.private_key,
                                                    sign_transaction=True)

    @property
    def optin(self, asset: Asset):
        opt_in_txn = ASATransactionRepository.asa_opt_in(
            client=self.client, sender_private_key=self.pk, asa_id=asset.asa_id
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=opt_in_txn)

    def buy(self, asset: Asset, seller: Account, amount: int):
        self.optin(asset)
        ## Atomic Transfer:
        
        # 1. Payment transaction: buyer -> seller

        asa_buy_payment_txn = PaymentTransactionRepository.payment(client=self.client,
                                                                   sender_address=self.address,
                                                                   receiver_address=seller.address,
                                                                   amount=amount,
                                                                   sender_private_key=None,
                                                                   sign_transaction=False)

        # 2. Asset transfer transaction: seller -> buyer

        asa_transfer_txn = ASATransactionRepository.asa_transfer(client=self.client,
                                                                 sender_address=seller.address,
                                                                 receiver_address=self.address,
                                                                 amount=1,
                                                                 asa_id=asset.asa_id,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)
        

        # Atomic transfer
        gid = transaction.calculate_group_id([asa_buy_payment_txn,
                                           asa_transfer_txn])

        asa_buy_payment_txn.group = gid
        asa_transfer_txn.group = gid

        asa_buy_txn_signed = asa_buy_payment_txn.sign(self.pk)
        asa_transfer_txn_signed = asa_transfer_txn.sign(seller.pk)

        signed_group = [asa_buy_txn_signed,
                        asa_transfer_txn_signed]

        tx_id = self.client.send_transactions(signed_group)

    def rent(self, asset: Asset, owner: Account, amount: int, duration: int):
        ### One thing to test is whether you can opt-in to an asset multiple times
        # TODO: perform tx
        
        self.optin(asset)
        
        asset.nft_renting_tool.make_rent_offer(amount, duration, owner.pk)
        asset.nft_renting_tool.rent_nft(self.address, self.pk, amount)
