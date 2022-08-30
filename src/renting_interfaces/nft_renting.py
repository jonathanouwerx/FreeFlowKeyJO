from abc import ABC, abstractmethod
### FIXED ###
# This is the parent class for interacting with the renting functionality
# The way this is currently structured is that the owner of an NFT offers up their 
# NFT to be rented for a specified period. Might be better to flip

class NFTRentingInterface(ABC):

    @abstractmethod
    def initialize_escrow(self, escrow_address, DAO_address):
        pass

    @abstractmethod
    def make_rent_offer(self, rent_price, rent_duration):
        pass

    @abstractmethod
    def rent(self):
        pass

    @abstractmethod
    def stop_rent_offer(self):
        pass

    # This is a new method which needs to be implemented
    @abstractmethod
    def recall_NFT(self):
        pass
