# Secure Multi-party Computation System

## Introduction

Secure Multi-Party Computation (SMC) is a cryptographic technique that enables multiple parties to jointly compute arithmetic circuit over their private inputs without exposing the underlying data. This framework supports essential operations such as the addition
and multiplication of both secret and scalar values, and it can
be seamlessly integrated into statistical model inference for
diverse parties.

You can find the project made by Clément Monera, Dominique Huang, Elia Mounier-Poulat for the CS-512 course at EPFL

#### Files

Components for building an SMC protocol:

* `expression.py`—Tools for defining arithmetic expressions.
* `secret_sharing.py`—Secret sharing scheme
* `ttp.py`—Trusted parameter generator for the Beaver multiplication scheme.
* `smc_party.py`—SMC party implementation
* `test_integration.py`—Integration test suite.
* `test_expression.py`—Template of a test suite for expression handling.
* `test_ttp.py`—Template of a test suite for the trusted parameter generator.
* `test_secret_sharing.py`—Template of a test suite for secret sharing.


Code that handles the communication:

* `protocol.py`—Specification of SMC protocol
* `communication.py`—SMC party-side of communication
* `server.py`—Trusted server to exchange information between SMC parties

Code that handles performance testing:

* `performance.py`—Code for testing the performance.
* `network_performances.py`—Code for testing the network performances.

Results files:

* `results`—Contains files of performance testing
* `plots`—Contains plots of performance testing

Application

* `test_application.py`—Code of an application of SMC
* `data_analysis.ipynb`—Analysis of data

#### Performance

You can launch each performance by calling the adequate function:
```
python3 performance.py
```

You can change the number of iteration in the `performance.py` file to iterate in order to compute the standard error.
To launch performance test in `performance.py`, you will need to uncomment the last lines of the file :

```
if __name__ == "__main__":
    sys.setrecursionlimit(3000)
    #test_operationperformance()
    #test_partyperformance()
    #plotting()
```

To launch `network_performances.py`, you might need to add arguments.

Disclaimer : THe performance tests might take a long time to run depending on the settings used.

#### Report

A report about was written 
