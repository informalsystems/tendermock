class Validator:
    def __init__(self, address: bytes, pubkey: bytes, power: int):
        self.address = address
        self.power = power
        self.pubkey = pubkey

    def setPower(self, power: int):
        self.power = power