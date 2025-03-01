"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

from typing import Dict, Set, Tuple

from secret_sharing import (
    share_secret,
    Share,
)

from random import getrandbits


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.triplet_shares: Dict[str, Dict[Tuple[Share, Share, Share]]] = {}

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        if op_id not in self.triplet_shares:
            self.generate_triplet(op_id)
        return self.triplet_shares[op_id][client_id]

    def generate_triplet(self, op_id: str):
        a = getrandbits(255)
        b = getrandbits(255)
        c = a * b
        number_of_participants = len(self.participant_ids)
        self.triplet_shares[op_id] = dict(
            zip(
                self.participant_ids,
                list(
                    zip(
                        share_secret(a, number_of_participants),
                        share_secret(b, number_of_participants),
                        share_secret(c, number_of_participants),
                    )
                ),
            )
        )
        print(self.triplet_shares)
