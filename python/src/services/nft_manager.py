
from src.blockchain_utils.transaction_repository import (
    ApplicationTransactionRepository,
    ASATransactionRepository,
    PaymentTransactionRepository,
)
from src.services.network_interaction import NetworkInteraction
from algosdk import logic as algo_logic
from algosdk.future import transaction as algo_txn
from pyteal import compileTeal, Mode
from algosdk.encoding import decode_address
from src.smart_contracts import NFTRentingASC1, nft_escrow

# TODO: Need to create functions for buying/selling, so that on the blockchain
# we have data stored showing that a certain NFT is up for rent.

# this is the main class which is created and used to rent NFTs.
# this is not the pyTEAL, it is just the python logic by which different parts of 
# the smart contract can be called and used.
class NFTManager:

    ##----------------Initialization----------------##

    def __init__(
            self, admin_pk, admin_address, nft_id, DAO_address, NFT_owner_address, client
    ):
        self.admin_pk = admin_pk
        self.admin_address = admin_address
        self.nft_id = nft_id
        self.DAO_address = DAO_address # RHS 2
        self.NFT_owner_address = NFT_owner_address

        self.client = client

        self.teal_version = 4
        self.nft_renting_asc1 = NFTRentingASC1()

        self.app_id = None

    @property
    def escrow_bytes(self):
        if self.app_id is None:
            raise ValueError("App not deployed")

        escrow_fund_program_compiled = compileTeal(
            nft_escrow(app_id=self.app_id, asa_id=self.nft_id),
            mode=Mode.Signature,
            version=4,
        )

        return NetworkInteraction.compile_program(
            client=self.client, source_code=escrow_fund_program_compiled
        )

    @property
    def escrow_address(self):
        return algo_logic.address(self.escrow_bytes)

    def app_initialization(self):
        approval_program_compiled = compileTeal(
            self.nft_renting_asc1.approval_program(),
            mode=Mode.Application,
            version=4,
        )

        clear_program_compiled = compileTeal(
            self.nft_renting_asc1.clear_program(),
            mode=Mode.Application,
            version=4
        )

        approval_program_bytes = NetworkInteraction.compile_program(
            client=self.client, source_code=approval_program_compiled
        )

        clear_program_bytes = NetworkInteraction.compile_program(
            client=self.client, source_code=clear_program_compiled
        )

        app_args = [
            decode_address(self.NFT_owner_address),
            decode_address(self.admin_address),
        ]

        app_transaction = ApplicationTransactionRepository.create_application(
            client=self.client,
            creator_private_key=self.admin_pk,
            approval_program=approval_program_bytes,
            clear_program=clear_program_bytes,
            global_schema=self.nft_renting_asc1.global_schema,
            local_schema=self.nft_renting_asc1.local_schema,
            app_args=app_args,
            foreign_assets=[self.nft_id], # LHS 2
        )

        tx_id = NetworkInteraction.submit_transaction(
            self.client, transaction=app_transaction
        )

        transaction_response = self.client.pending_transaction_info(tx_id)

        self.app_id = transaction_response["application-index"]

        return tx_id

    def initialize_escrow(self):
        app_args = [
            self.nft_renting_asc1.AppMethods.initialize_escrow,
            decode_address(self.escrow_address), 
            self.DAO_address # RHS 1
        ]

        print(f"init_escrow Dao address: {self.DAO_address}")

        initialize_escrow_txn = ApplicationTransactionRepository.call_application(
            client=self.client,
            caller_private_key=self.admin_pk,
            app_id=self.app_id,
            on_complete=algo_txn.OnComplete.NoOpOC,
            app_args=app_args,
            foreign_assets=[self.nft_id],
        )

        tx_id = NetworkInteraction.submit_transaction(
            self.client, transaction=initialize_escrow_txn
        )

        return tx_id

    def fund_escrow(self):
        fund_escrow_txn = PaymentTransactionRepository.payment(
            client=self.client,
            sender_address=self.admin_address,
            receiver_address=self.escrow_address,
            amount=1000000, ### this amount needs to be checked and changed
            sender_private_key=self.admin_pk,
            sign_transaction=True,
        )

        tx_id = NetworkInteraction.submit_transaction(
            self.client, transaction=fund_escrow_txn
        )

        return tx_id

    ##----------------Buying----------------##

    def buy_nft(self, buyer_address, buyer_pk, nft_owner_pk, amount):
        ## Atomic Transfer:
        
        # 1. Payment transaction: buyer -> seller

        asa_buy_payment_txn = PaymentTransactionRepository.payment(client=self.client,
                                                                   sender_address=buyer_address,
                                                                   receiver_address=self.nft_owner_address,
                                                                   amount=amount,
                                                                   sender_private_key=None,
                                                                   sign_transaction=False)

        # 2. Asset transfer transaction: seller -> buyer

        asa_transfer_txn = ASATransactionRepository.asa_transfer(client=self.client,
                                                                 sender_address=self.nft_owner_address,
                                                                 receiver_address=buyer_address,
                                                                 amount=1,
                                                                 asa_id=self.asa_id,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)
        

        # Atomic transfer
        gid = algo_txn.calculate_group_id([asa_buy_payment_txn,
                                           asa_transfer_txn])

        asa_buy_payment_txn.group = gid
        asa_transfer_txn.group = gid

        asa_buy_txn_signed = asa_buy_payment_txn.sign(buyer_pk)
        asa_transfer_txn_signed = asa_transfer_txn.sign(nft_owner_pk)

        signed_group = [asa_buy_txn_signed,
                        asa_transfer_txn_signed]

        tx_id = self.client.send_transactions(signed_group)

    ##----------------Renting----------------##   

    def make_rent_offer(self, rent_price: int, rent_duration: int, nft_owner_pk):
        app_args = [self.nft_renting_asc1.AppMethods.make_rent_offer, rent_price, rent_duration]

        app_call_txn = ApplicationTransactionRepository.call_application(
            client=self.client,
            caller_private_key=nft_owner_pk,
            app_id=self.app_id,
            on_complete=algo_txn.OnComplete.NoOpOC,
            app_args=app_args,
            sign_transaction=True,
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=app_call_txn)
        return tx_id

    def rent_nft(self, renter_address, renter_pk, rent_price):

        # 1. Application call transaction: renter calls application

        app_args = [
            self.nft_renting_asc1.AppMethods.rent,
            1 # sends a True value in this send_asa bool field
        ]

        app_call_txn = ApplicationTransactionRepository.call_application(client=self.client,
                                                                         caller_private_key=renter_pk,
                                                                         app_id=self.app_id,
                                                                         on_complete=algo_txn.OnComplete.NoOpOC,
                                                                         app_args=app_args,
                                                                         sign_transaction=False)

        # 2. Payment transaction: renter -> rentee

        asa_buy_payment_txn = PaymentTransactionRepository.payment(client=self.client,
                                                                   sender_address=renter_address,
                                                                   receiver_address=self.nft_owner_address,
                                                                   amount=rent_price,
                                                                   sender_private_key=None,
                                                                   sign_transaction=False)

        # 3. Asset transfer transaction: escrow -> renter

        asa_transfer_txn = ASATransactionRepository.asa_transfer(client=self.client,
                                                                 sender_address=self.escrow_address,
                                                                 receiver_address=renter_address,
                                                                 amount=1,
                                                                 asa_id=self.nft_id,
                                                                 revocation_target=self.nft_owner_address,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)
    
        # 4. Asset freeze transaction: escrow freezing renter

        asa_freeze_txn = ASATransactionRepository.change_freeze_asa(client=self.client,
                                                                 sender_address=self.escrow_address,
                                                                 target_address=renter_address,
                                                                 asa_id=self.nft_id,
                                                                 freeze_bool=True,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)

        # Atomic transfer
        gid = algo_txn.calculate_group_id([app_call_txn,
                                           asa_buy_payment_txn,
                                           asa_transfer_txn,
                                           asa_freeze_txn])

        app_call_txn.group = gid
        asa_buy_payment_txn.group = gid
        asa_transfer_txn.group = gid
        asa_freeze_txn.group = gid

        app_call_txn_signed = app_call_txn.sign(renter_pk)

        asa_buy_txn_signed = asa_buy_payment_txn.sign(renter_pk)

        asa_transfer_txn_logic_signature = algo_txn.LogicSig(self.escrow_bytes)
        asa_transfer_txn_signed = algo_txn.LogicSigTransaction(asa_transfer_txn, asa_transfer_txn_logic_signature)

        asa_freeze_txn_logic_signature = algo_txn.LogicSig(self.escrow_bytes)
        asa_freeze_txn_signed = algo_txn.LogicSigTransaction(asa_freeze_txn, asa_freeze_txn_logic_signature)

        signed_group = [app_call_txn_signed,
                        asa_buy_txn_signed,
                        asa_transfer_txn_signed,
                        asa_freeze_txn_signed]

        tx_id = self.client.send_transactions(signed_group)
        return tx_id

    def stop_rent_offer(self, nft_owner_pk):
        app_args = [self.nft_renting_asc1.AppMethods.stop_rent_offer]

        app_call_txn = ApplicationTransactionRepository.call_application(
            client=self.client,
            caller_private_key=nft_owner_pk,
            app_id=self.app_id,
            on_complete=algo_txn.OnComplete.NoOpOC,
            app_args=app_args,
            sign_transaction=True,
        )

        tx_id = NetworkInteraction.submit_transaction(self.client, transaction=app_call_txn)
        return tx_id

    def recall_nft(self, renter_address, nft_owner_pk):

        # 1. Application call transaction: rentee calls application

        app_args = [
            self.nft_renting_asc1.AppMethods.recall_NFT,
            0 # sends a False value in this send_asa bool field
        ]

        app_call_txn = ApplicationTransactionRepository.call_application(client=self.client,
                                                                         caller_private_key=nft_owner_pk,
                                                                         app_id=self.app_id,
                                                                         on_complete=algo_txn.OnComplete.NoOpOC,
                                                                         app_args=app_args,
                                                                         sign_transaction=False)

        # 2. Asset transfer transaction: escrow -> rentee

        asa_transfer_txn = ASATransactionRepository.asa_transfer(client=self.client,
                                                                 sender_address=self.escrow_address,
                                                                 receiver_address=self.nft_owner_address,
                                                                 amount=1,
                                                                 asa_id=self.nft_id,
                                                                 revocation_target=self.nft_owner_address,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)
    
        # 3. Asset freeze transaction: escrow unfreezing renter

        asa_freeze_txn = ASATransactionRepository.change_freeze_asa(client=self.client,
                                                                 sender_address=self.escrow_address,
                                                                 target_address=renter_address,
                                                                 asa_id=self.nft_id,
                                                                 freeze_bool=False,
                                                                 sender_private_key=None,
                                                                 sign_transaction=False)

        # Atomic transfer
        gid = algo_txn.calculate_group_id([app_call_txn,
                                           asa_transfer_txn,
                                           asa_freeze_txn])

        app_call_txn.group = gid
        asa_transfer_txn.group = gid
        asa_freeze_txn.group = gid

        app_call_txn_signed = app_call_txn.sign(nft_owner_pk)

        asa_transfer_txn_logic_signature = algo_txn.LogicSig(self.escrow_bytes)
        asa_transfer_txn_signed = algo_txn.LogicSigTransaction(asa_transfer_txn, asa_transfer_txn_logic_signature)

        asa_freeze_txn_logic_signature = algo_txn.LogicSig(self.escrow_bytes)
        asa_freeze_txn_signed = algo_txn.LogicSigTransaction(asa_freeze_txn, asa_freeze_txn_logic_signature)

        signed_group = [app_call_txn_signed,
                        asa_transfer_txn_signed,
                        asa_freeze_txn_signed]

        tx_id = self.client.send_transactions(signed_group)
        return tx_id
