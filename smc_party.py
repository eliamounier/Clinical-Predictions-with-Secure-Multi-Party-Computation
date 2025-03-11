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
from expression import *
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
        parties = self.protocol_spec.participant_ids
        num_shares = len(parties)

        for secret in self.value_dict:
            shares = share_secret(self.value_dict[secret], num_shares)
            for i, party in enumerate(parties):
                self.comm.send_private_message(party, secret.id, shares[i].serialize())
        
        # Step 2: Receive the shares.
        self.shares_dict: Dict[str, Share] = {}

        self.process_expression(expr)
        shares = [Share.deserialize(self.comm.retrieve_public_message(sender_id, expr.id)) for sender_id in self.protocol_spec.participant_ids]
        result = reconstruct_secret(shares)
        print(result)
        return result

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ) -> Share:
        if isinstance(expr, AddOp):
            a = self.process_expression(expr.a)
            b = self.process_expression(expr.b)
            new_share = (a + b).withId(expr.id)
            self.comm.publish_message(expr.id, new_share.serialize())
            return new_share
        
      
        elif isinstance(expr, MulOp):
            s = self.process_expression(expr.a)
            v = self.process_expression(expr.b)
            a_beav, b_beav, c_beav = self.comm.retrieve_beaver_triplet_shares(expr.id)

            # Step 1. "Each party computes locally a share of [d] = [s-a] and broadcasts it. Then each party reconstructs d."
            d = s - a_beav
            self.comm.publish_message(f"d_{expr.id}", d.serialize())
            d_shares = [Share.deserialize(self.comm.retrieve_public_message(sender_id, f"d_{expr.id}")) for sender_id in self.protocol_spec.participant_ids]
            d_val = reconstruct_secret(d_shares)
            
            # Step 2. " Each party computes locally a share of [e] = [v-b] and broadcasts it. Then each party reconstructs e."  
            e = v - b_beav
            self.comm.publish_message(f"e_{expr.id}", e.serialize())
            e_shares = [Share.deserialize(self.comm.retrieve_public_message(sender_id, f"e_{expr.id}")) for sender_id in self.protocol_spec.participant_ids]
            e_val = reconstruct_secret(e_shares)

            # Step 3. Locally computes: [t] = [c] + [s]*[e] + [v]*[d] - [d]*[e]
            t = c_beav + (s*e_val) + (v*d_val) 
            
            if self.protocol_spec.participant_ids.index(self.client_id) == 0: # Only one party should add the constant term [d]*[e]
                t -= Share(d_val * e_val, t.id) #

            t = t.withId(expr.id)
            self.comm.publish_message(expr.id, t.serialize())
            return t
        
        elif isinstance(expr, SubOp):
            a = self.process_expression(expr.a)
            b = self.process_expression(expr.b)
            new_share = (a - b).withId(expr.id)
            self.comm.publish_message(expr.id, new_share.serialize())
            return new_share
        
        elif isinstance(expr, Secret):
            if expr.id not in self.shares_dict:
                share = Share.deserialize(self.comm.retrieve_private_message(expr.id))
                self.shares_dict[expr.id] = share
            return self.shares_dict[expr.id]
        elif isinstance(expr, Scalar):
            if self.protocol_spec.participant_ids.index(self.client_id) == 0:
                return Share(expr.value, id=expr.id)
            else:
                return Share(0, id=expr.id)
        else:
            raise ValueError(f"Unknown expression type: {expr}")
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.


    # Feel free to add as many methods as you want.
