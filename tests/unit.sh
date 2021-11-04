#!/bin/bash

python tests/unit_mambuconfig.py
python tests/unit_mambutask.py
python tests/unit_mamburoles.py
python tests/unit_mamburepayment.py
python tests/unit_mambuproduct.py
python tests/unit_mambucentre.py
python tests/unit_mambubranch.py
python tests/unit_mambuactivity.py
python tests/unit_mambutransaction.py
python tests/unit_mambuuser.py
python tests/unit_mambustruct.py
python tests/unit_mambugroup.py
python tests/unit_mambuclient.py
python tests/unit_mambuutil.py
python tests/unit_mambuloan.py

python tests/api/unit_mambuconnector.py
python tests/api/unit_mambustruct.py
python tests/api/unit_mambuloan.py
