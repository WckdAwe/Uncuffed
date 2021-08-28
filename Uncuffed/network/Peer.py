class Peer:
    def __init__(self, address: str, port: int):
        """
        Peer entity.
        Each peer is basically a node that we can send/receive information.
        :param address: IP Address of the peer
        :param port: Port of the peer
        """
        self.address: str = address
        self.port: int = port

    @classmethod
    def from_string(cls, address: str):
        """
        Convert an address with format of {ip}:{port} to a Peer Object
        :param address:
        :return: Peer Object
        """
        addr, port = address.split(':', 1)
        return cls(
            address=addr,
            port=port,
        )

    def get_url(self, use_https=False) -> str:
        protocol = 'https' if use_https else 'http'
        return f'{protocol}://{str(self)}'

    def __str__(self):
        return f'{self.address}:{self.port}'

    def __hash__(self):
        return hash((self.address, self.port))

    def __eq__(self, other):
        if not isinstance(other, Peer):
            return NotImplemented

        return self.address == other.address and self.port == other.port
