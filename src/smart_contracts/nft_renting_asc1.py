from pyteal import *
import algosdk

### ALMOST FIXED ###

'''
TO DO LIST:
- Introduce the freezing of the asset
- read through the rest of the main README
- Check why, in initialise escrow, the addresses are stated
- figure out a way to evaluate the time within the smart contract
- work out the associated transactions and structures that need to take place and exist
'''


from src.renting_interfaces import NFTRentingInterface


class NFTRentingASC1(NFTRentingInterface):
    class Variables:
        escrow_address = Bytes("ESCROW_ADDRESS")
        DAO_address = Bytes("DAO_ADDRESS")
        asa_id = Bytes("ASA_ID")
        asa_price = Bytes("ASA_PRICE")
        asa_duration = Bytes("ASA_DURATION")
        asa_owner = Bytes("ASA_OWNER")
        app_state = Bytes("APP_STATE")
        app_admin = Bytes("APP_ADMIN")

    class AppMethods:
        initialize_escrow = "initializeEscrow"
        make_rent_offer = "makeRentOffer"
        rent = "Rent"
        stop_rent_offer = "stopRentOffer"
        recall_NFT = "recallNFT"

    class AppState:
        not_initialized = Int(0)
        active = Int(1)
        up_for_rent = Int(2)
        renting = Int(3)

    def application_start(self):
        actions = Cond(
            [Txn.application_id() == Int(0), self.app_initialization()],

            [Txn.application_args[0] == Bytes(self.AppMethods.initialize_escrow),
             self.initialize_escrow(escrow_address=Txn.application_args[1], DAO_address=Txn.application_args[2])],

            [Txn.application_args[0] == Bytes(self.AppMethods.make_rent_offer),
             self.make_rent_offer(rent_price=Txn.application_args[1], rent_duration=application_args[2])],

            [Txn.application_args[0] == Bytes(self.AppMethods.rent),
             self.rent()],

            [Txn.application_args[0] == Bytes(self.AppMethods.stop_rent_offer), self.stop_rent_offer()],

            [Txn.application_args[0] == Bytes(self.AppMethods.recall_NFT), self.recall_NFT()]
        )

        return actions

    def app_initialization(self):
        """
        CreateAppTxn with 2 arguments: asa_owner, app_admin.
        The foreign_assets array should have 1 asa_id which will be the id of the NFT of interest.
        :return:
        """
        return Seq([
            Assert(Txn.application_args.length() == Int(2)),
            App.globalPut(self.Variables.app_state, self.AppState.not_initialized),
            App.globalPut(self.Variables.asa_id, Txn.assets[0]),
            App.globalPut(self.Variables.asa_owner, Txn.application_args[0]),
            App.globalPut(self.Variables.app_admin, Txn.application_args[1]),
            Return(Int(1))
        ])

    def initialize_escrow(self, escrow_address, DAO_address):
        """
        Application call from the app_admin.
        :return:
        """
        curr_escrow_address = App.globalGetEx(Int(0), self.Variables.escrow_address)

        asset_escrow = AssetParam.clawback(Txn.assets[0])
        DAO_manager = AssetParam.manager(Txn.assets[0])
        freeze_address = AssetParam.freeze(Txn.assets[0])
        reserve_address = AssetParam.reserve(Txn.assets[0])
        default_frozen = AssetParam.defaultFrozen(Txn.assets[0])

        return Seq([
            curr_escrow_address,
            Assert(curr_escrow_address.hasValue() == Int(0)),

            Assert(App.globalGet(self.Variables.app_admin) == Txn.sender()),
            Assert(Global.group_size() == Int(1)),

            asset_escrow,
            DAO_manager,
            freeze_address,
            reserve_address,
            default_frozen,
            Assert(Txn.assets[0] == App.globalGet(self.Variables.asa_id)),
            Assert(asset_escrow.value() == Txn.application_args[1]), 
            Assert(default_frozen.value() == False),
            Assert(DAO_manager.value() == Txn.application_args[2]),
            Assert(freeze_address.value() == Txn.application_args[1]),
            Assert(reserve_address.value() == Global.zero_address()),

            App.globalPut(self.Variables.escrow_address, escrow_address),
            App.globalPut(self.Variables.DAO_address, DAO_address),
            App.globalPut(self.Variables.app_state, self.AppState.active),
            Return(Int(1))
        ])

    def make_rent_offer(self, rent_price, rent_duration):
        """
        Single application call with 3 arguments.
        - method_name
        - price
        - duration
        :return:
        """
        valid_number_of_transactions = Global.group_size() == Int(1)
        app_is_active = Or(App.globalGet(self.Variables.app_state) == self.AppState.active,
                           App.globalGet(self.Variables.app_state) == self.AppState.up_for_rent)

        valid_rentee = Txn.sender() == App.globalGet(self.Variables.asa_owner)
        valid_number_of_arguments = Txn.application_args.length() == Int(3)

        can_rent = And(valid_number_of_transactions,
                       app_is_active,
                       valid_rentee,
                       valid_number_of_arguments)

        update_state = Seq([
            App.globalPut(self.Variables.asa_price, Btoi(rent_price)),
            App.globalPut(self.Variables.asa_duration, Btoi(rent_duration)),
            App.globalPut(self.Variables.app_state, self.AppState.up_for_rent),
            Return(Int(1))
        ])

        return If(can_rent).Then(update_state).Else(Return(Int(0)))

    def rent(self):
        """
        Atomic transfer of 3 transactions:
        1. Application call.
        2. Payment from renter to rentee.
        3. Asset transfer from escrow to renter.
        :return:
        """
        valid_number_of_transactions = Global.group_size() == Int(3)
        asa_is_up_for_rent = App.globalGet(self.Variables.app_state) == self.AppState.up_for_rent

        valid_payment_to_rentee = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.asa_owner),
            Gtxn[1].amount() == App.globalGet(self.Variables.asa_price),
            Gtxn[1].sender() == Gtxn[0].sender(),
            Gtxn[1].sender() == Gtxn[2].asset_receiver()
        )

        valid_asa_transfer_from_escrow_to_renter = And(
            Gtxn[2].type_enum() == TxnType.AssetTransfer,
            Gtxn[2].sender() == App.globalGet(self.Variables.escrow_address),
            Gtxn[2].xfer_asset() == App.globalGet(self.Variables.asa_id),
            Gtxn[2].asset_amount() == Int(1)
        )

        can_rent = And(valid_number_of_transactions,
                      asa_is_up_for_rent,
                      valid_payment_to_rentee,
                      valid_asa_transfer_from_escrow_to_renter)

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.renting),
            Return(Int(1))
        ])

        return If(can_rent).Then(update_state).Else(Return(Int(0)))

    def stop_rent_offer(self):
        """
        Single application call.
        :return:
        """
        valid_number_of_transactions = Global.group_size() == Int(2)
        valid_caller = Txn.sender() == App.globalGet(self.Variables.asa_owner)
        app_is_initialized = App.globalGet(self.Variables.app_state) != self.AppState.not_initialized

        can_stop_offering = And(valid_number_of_transactions,
                               valid_caller,
                               app_is_initialized)

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.active),
            Return(Int(1))
        ])

        return If(can_stop_offering).Then(update_state).Else(Return(Int(0)))

    # I need to unfreeze the asset
    # I need to check that the rent_period_elapsed
    # I need to allow the DAO to recall this within the rent_period
    def recall_NFT(self):
        '''
        This is much more complicated

        I need to have some way for the contract to access the elapsed time. 
        '''

        """
        Double application call.
        1. Application call.
        2. Asset transfer from escrow to rentee.
        :return:
        """

        valid_number_of_transactions = Global.group_size() == Int(1)

        asa_is_rented = App.globalGet(self.Variables.app_state) == self.AppState.renting

        # This needs to be solved
        rent_period_elapsed = False
        
        valid_asa_transfer_from_escrow_to_rentee = And(
            Gtxn[1].type_enum() == TxnType.AssetTransfer,
            Gtxn[1].sender() == App.globalGet(self.Variables.escrow_address),
            Gtxn[1].xfer_asset() == App.globalGet(self.Variables.asa_id),
            Gtxn[1].asset_amount() == Int(1)
            Gtxn[1].asset_receiver() == App.globalGet(self.Variables.asa_owner)
            )  

        can_recall_NFT = And(valid_number_of_transactions,
                            asa_is_rented,
                            rent_period_elapsed,
                            valid_asa_transfer_from_escrow_to_rentee)

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.active),
            Return(Int(1))
        ])

        return If(can_recall_NFT).Then(update_state).Else(Return(Int(0)))



    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))

    @property
    def global_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=4,
                                                      num_byte_slices=4)

    @property
    def local_schema(self):
        return algosdk.future.transaction.StateSchema(num_uints=0,
                                                      num_byte_slices=0)
