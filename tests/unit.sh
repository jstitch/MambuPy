#!/bin/bash

tests=("unit_mambuconfig.py" \
           "unit_mambutask.py" \
           "unit_mamburoles.py" \
           "unit_mamburepayment.py" \
           "unit_mambuproduct.py" \
           "unit_mambucentre.py" \
           "unit_mambubranch.py" \
           "unit_mambuactivity.py" \
           "unit_mambutransaction.py" \
           "unit_mambuuser.py" \
           "unit_mambustruct.py" \
           "unit_mambugroup.py" \
           "unit_mambuclient.py" \
           "unit_mambuutil.py" \
           "unit_mambuloan.py" \
           "api/unit_mambuconnector.py" \
           "api/unit_mambustruct.py" \
           "api/unit_mambuloan.py" \
      )
for test in ${tests[@]}
do
    echo $test
    python tests/$test
    echo ""
done
