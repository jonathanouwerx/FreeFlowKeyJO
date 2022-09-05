from pyteal import *

### ALMOST FIXED ###

def nft_escrow(app_id: int, asa_id: int):

    send_asa = Seq([

        Assert(Global.group_size() == Int(4)),
        # asserts that the stateful smart contract is called in the atomic transfer
        # ensures that its logic must succeed for the escrow account to transfer assets
        Assert(Gtxn[0].application_id() == Int(app_id)), 

        # the following code seems like a redundancy
        Assert(Gtxn[1].type_enum() == TxnType.Payment),

        Assert(Gtxn[2].asset_amount() == Int(1)),
        Assert(Gtxn[2].xfer_asset() == Int(asa_id)),
        Assert(Gtxn[2].fee() <= Int(1000)), # is this line desired?
        Assert(Gtxn[2].asset_close_to() == Global.zero_address()), # check what this does
        Assert(Gtxn[2].rekey_to() == Global.zero_address()), # check what this does

        Assert(Gtxn[3].type_enum() == TxnType.AssetFreeze),
        Assert(Gtxn[3].freeze_asset() == Int(asa_id)),
        Assert(Gtxn[3].freeze_asset_frozen() == Int(1)),
        
        Return(Int(1))
    ])

    return_asa = Seq([

        Assert(Global.group_size() == Int(3)),
        # asserts that the stateful smart contract is called in the atomic transfer
        # ensures that its logic must succeed for the escrow account to transfer assets
        Assert(Gtxn[0].application_id() == Int(app_id)), 

        Assert(Gtxn[1].asset_amount() == Int(1)),
        Assert(Gtxn[1].xfer_asset() == Int(asa_id)),
        Assert(Gtxn[1].fee() <= Int(1000)), # is this line desired?
        Assert(Gtxn[1].asset_close_to() == Global.zero_address()), # check what this does
        Assert(Gtxn[1].rekey_to() == Global.zero_address()), # check what this does

        Assert(Gtxn[3].type_enum() == TxnType.AssetFreeze),
        Assert(Gtxn[3].freeze_asset() == Int(asa_id)),
        Assert(Gtxn[3].freeze_asset_frozen() == Int(0)),

        Return(Int(1))
    ])

    # the below conditions should work, but need to check location is correct and in general
    # alternative is to assert that the state of the smart contract is up_for_rent/rented
    # alternative is more robust but more difficult

    return Cond([Gtxn[0].app_args[1] == "send_asa", send_asa],
                [Gtxn[0].app_args[1] == "return_asa", return_asa])


