"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""

from secret_sharing import *

def test():
    test_values = [1, 8, 7455, 2, 847, -48, -984]
    for value in test_values:
        assert reconstruct_secret(share_secret(value, 7)) == value