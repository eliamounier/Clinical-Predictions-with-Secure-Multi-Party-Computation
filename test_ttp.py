"""
Unit tests for the trusted parameter generator.
Testing ttp is not obligatory.

MODIFY THIS FILE.
"""

from ttp import TrustedParamGenerator
from random import shuffle

def test():
    ttp = TrustedParamGenerator()
    participant_ids = ["Monkey", "Banana", "Jar Jar Binks", "Shrek", "Broccoli"]
    for participant_id in participant_ids:
        ttp.add_participant(participant_id)
    
    operation_ids = ["Go to la Migros", "Buy Bananas", "Make banana cake", "Eat banana cake"]
    for op_id in operation_ids:
        a, b, c = 0, 0, 0
        shuffled_ids = list(participant_ids)
        shuffle(shuffled_ids)
        for participant_id in shuffled_ids:
            a_i, b_i, c_i = ttp.retrieve_share(participant_id, op_id)
            a += a_i.value
            b += b_i.value
            c += c_i.value
        assert a * b == c
