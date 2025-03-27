"""
Test file demonstrating a medical application of SMC where multiple hospitals
collaboratively compute a machine learning inference without revealing patient data.

Example model: Predict the probability of a patient needing to be transferred to a more
specialized hospital based on their 'sensitive' medical history collected across different
healthcare facilities.
"""

import time
from multiprocessing import Process, Queue
import math

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run
from smc_party import SMCParty       


from test_integration import suite, smc_server


def test_hospital_ml_inf_1():
    """
    f([a1, a2], [b1], [c1, c2]) = a1 - b1 + c1 + a2*c2
    """
    hospA_secret = [Secret(), Secret()]  
    hospB_secret = Secret()             
    hospC_secret = [Secret(), Secret()] 

    parties = {
        "HospitalA": {
            hospA_secret[0]: 1,  
            hospA_secret[1]: 3   
        },
        "HospitalB": {
            hospB_secret: 4     
        },
        "HospitalC": {
            hospC_secret[0]: 2,  
            hospC_secret[1]: 3  
        }
    }

    
    expr = (hospA_secret[0] - hospB_secret + hospC_secret[0] +  hospA_secret[1] * hospC_secret[1])
    expected = 1 - 4 + 2 + (3 * 3)
    suite(parties, expr, expected)


def test_hospital_ml_inf_2():
    """
    f([a1, a2, a3], [b1, b2], [c1, c2]) =  w0 + w1*a1 + w2*b1 + w3*c1 + w4*(a2*b2) + w5*(c2*a3) 
    """
    hospA_secret = [Secret(), Secret(), Secret()]  
    hospB_secret = [Secret(), Secret()]                 
    hospC_secret = [Secret(), Secret()]             

    parties = {
        "HospitalA": {
            hospA_secret[0]: 100,  
            hospA_secret[1]: 3,  
            hospA_secret[2]: 2  
        },
        "HospitalB": {
            hospB_secret[0]: 4,  
            hospB_secret[1]: 58   
        },
        "HospitalC": {
            hospC_secret[0]: 2,  
            hospC_secret[1]: 34   
        }
    }     

    expr = (
        Scalar(1) +
        (Scalar(2) * hospA_secret[0]) +
        (Scalar(3) * hospB_secret[0]) +
        (Scalar(4) * hospC_secret[0]) +
        (Scalar(5) * hospA_secret[1] * hospB_secret[1]) +
        (Scalar(6) * hospC_secret[1] * hospA_secret[2])
    )                               

    expected = (1 + (2 * 100) + (3 * 4) + (4 * 2) + (5 * (3 * 58)) + (6 * (34 * 2)))                   

    suite(parties, expr, expected)      


