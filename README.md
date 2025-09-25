# An SMC Framework for Privacy-Preserving Clinical Prediction Across Hospitals

**Authors:** Clément Moréna, Dominique Huang, Élia Mounier-Poulat  
**Course Project:** EPFL – Secure Multi-Party Computation  
**Date:** 2025  

---

## 📘 Overview
This project implements a **Secure Multi-Party Computation (SMC)** framework that enables multiple hospitals to jointly compute medical predictions **without sharing sensitive patient data**.  

We evaluate performance in terms of computation and communication cost, and demonstrate how the framework can support clinical decision-making (e.g., computing patient risk scores across distributed records).

---

## 🧠 Key Features
- Additive secret sharing in a finite field  
- Secure addition and multiplication (via Beaver triplets)  
- Performance analysis with up to 50 parties  
- Example application: privacy-preserving clinical risk scoring  

---

## 🗂️ Project Skeleton
We implemented the SMC client, the trusted parameter generator, secret sharing mechanisms, and tools for specifying expressions to compute.  

Main files:
- `expression.py` — Tools for defining arithmetic expressions  
- `secret_sharing.py` — Additive secret sharing scheme  
- `ttp.py` — Trusted parameter generator (Beaver triplets)  
- `smc_party.py` — Implementation of an SMC party  
- `test_integration.py` — Integration test suite  
- `test_expression.py`, `test_ttp.py`, `test_secret_sharing.py` — Unit test templates  

Files to handle communication & protocol:  
- `protocol.py`  
- `communication.py`  
- `server.py`  

---

## 🧪 Installation & Testing

This code was implemented and tested with Python 3.9, you may want to install a
higher version, in which case, ensure that you only use features supported by
Python 3.9 in your code.

You can install the dependant python libraries by running the command
```
python3 -m pip install -r requirements.txt
```
Run all tests:
```
python3 -m pytest
```


