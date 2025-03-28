"""
Secret sharing scheme.
"""

from __future__ import annotations

from typing import List, Optional
import random
import base64

import json

ID_BYTES = 4

def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value: int, id: Optional[bytes] = None):
        if id is None:
            id = gen_id()
        self.id = id
        self.value = value % Share.prime()

    def __repr__(self):
        # Helps with debugging.
        return f"Share({self.value}, {self.id})"

    def __add__(self, other):
        return Share(self.value + other.value)

    def __sub__(self, other):
        return Share(self.value - other.value)

    def __mul__(self, other):
        if isinstance(other, Share):
            return Share(self.value * other.value, self.id)
        else:
            return Share(self.value * other, self.id) # scalar multiplication


    def withId(self, new_id: bytes):
        return Share(self.value, new_id)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return json.dumps({'id': self.id.hex(), 'value': self.value})

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        data = json.loads(serialized)
        return Share(data['value'], bytes.fromhex(data['id']))
    
    @staticmethod
    def prime() -> int:
        return 10000013983
    
def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = [random.randint(-abs(secret), abs(secret)) for _ in range(num_shares - 1)]
    last_share = secret - sum(shares)
    shares.append(last_share)
    return list(map(lambda value: Share(value), shares))

def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for share in shares:
        secret += share.value
    return secret % Share.prime()


# Feel free to add as many methods as you want.
