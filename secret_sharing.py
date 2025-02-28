"""
Secret sharing scheme.
"""

from __future__ import annotations

from typing import List
import random
import time
import base64

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
        self.value = value

    def __repr__(self):
        # Helps with debugging.
        return f"Share({self.value}, {self.id})"
        #raise NotImplementedError("You need to implement this method.")

    def __add__(self, other):
        return Share(self.value + other.value, self.id)
        #raise NotImplementedError("You need to implement this method.")

    def __sub__(self, other):
        return Share(self.value - other.value, self.id)
        #raise NotImplementedError("You need to implement this method.")

    def __mul__(self, other):
        return Share(self.value * other.value, self.id)
        #raise NotImplementedError("You need to implement this method.")

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        raise NotImplementedError("You need to implement this method.")

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        raise NotImplementedError("You need to implement this method.")


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    share = []
    seed = time.time()
    random.seed(seed)

    for i in range(num_shares -1):
        val = random.randint(0, secret)
        share.append(Share(val))
        secret -= val
    share.append(Share(secret))
    return share

    #raise NotImplementedError("You need to implement this method.")


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for share in shares:
        secret += share.value
    return secret
    #raise NotImplementedError("You need to implement this method.")


# Feel free to add as many methods as you want.

print(share_secret(10, 3))
print(reconstruct_secret(share_secret(10, 3)))
for i in range(3):
    print(share_secret(10, 3)[i].id)
