'''

OPTION 1: SMART CONTRACT

Brief: Create a statefull application which is tied to a certain account and is
required to sign in order for the account to purchase any FFKs
(similar to FFK idea, will require unique hash linked to application ID, unless
applications also have a unique creator address)

methods:
- all the standard methods
- NoOp call
    - purchase validation
        - needs to be grouped with FFK stateful call (+ all those txns)
          and % payment to referees
    - rent validation
        - needs to be grouped with FFK stateful call (+ all those txns)
          and % payment to referees

global variables
- account
- referee
- referee commission
- grand referee
- grand referee commission

This begins to create quite a complex web of transactions and will require the 
existing interfaces for renting and so on to be modified. Will require buying/selling
to be controlled by smart contracts as well ie default_frozen = True

OPTION 2: One level of referee

in the atomic transfer of payment and asset, a third payment to a designated address
should be added. or rather the buyer's payment should be split in two.

'''