"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict


    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """

        expr = self.protocol_spec.expr

        # Step 1: Share the secrets.
        parties = self.protocol_spec.participants_ids
        num_shares = len(parties)

        for secret in self.value_dict:
            shares = share_secret(self.value_dict[secret], num_shares)
            for i, party in enumerate(parties):
                self.comm.send_private_message(party, secret.id,shares[i])
        
        # Step 2: Receive the shares.
        shares_dict = collections.defaultdict(dict)
        for party in parties:
            for secret in self.value_dict:
                label = secret.id
                message = self.comm.retrieve_private_message(self.client_id, label)
                shares_dict[party][secret] = message

        # Step 3: Process the expression.
        for party in parties:
            self.shares_dict = shares_dict
            result = self.process_expression(expr)
            self.comm.send_public_message(party, expr.id, result)


        raise NotImplementedError("You need to implement this method.")


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):
        if isinstance(expr, AddOp):
            self.process_add_op(expr)
        elif isinstance(expr, MulOp):
            self.process_mul_op(expr)
        elif isinstance(expr, SubOp):
            self.process_sub_op(expr)
        elif isinstance(expr, Secret):
            self.process_secret(expr)
        elif isinstance(expr, Scalar):
            self.process_scalar(expr)
        else:
            raise ValueError(f"Unknown expression type: {expr}")
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
    
    def process_add_op(self, expr: AddOp):
        a = self.process_expression(expr.left)
        b = self.process_expression(expr.right)
        # Process further the left and right sub-expressions of the addition operation.
        return a + b

    def process_mul_op(self, expr: MulOp):
        a = self.process_expression(expr.left)
        b = self.process_expression(expr.right)
        # Process further the left and right sub-expressions of the multiplication operation.
        return a * b
    
    def process_sub_op(self, expr: SubOp):
        a = self.process_expression(expr.left)
        b = self.process_expression(expr.right)
        # Process further the left and right sub-expressions of the subtraction operation.
        return a - b

    def process_secret(self, expr: Secret, party_id: str):
        # Process the secret expression.

        return self.shares_dict[party_id][expr]
    
    def process_scalar(self, expr: Scalar):
        # Process the scalar expression.
        return expr.value
    



    # Feel free to add as many methods as you want.
