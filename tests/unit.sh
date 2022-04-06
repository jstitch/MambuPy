#!/bin/bash
OPTIND=1
apiv2="apiv2"
while getopts "a:" opt; do
    case "$opt" in
        a)
            apiv2=$OPTARG
            ;;
    esac
done

rm -f .coverage
rm -rf htmlcov
rm -f coverage.xml

fails=0

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
           "api/unit_mambugroup.py" \
           "api/unit_mambuclient.py" \
           "api/unit_mambubranch.py" \
           "api/unit_mambucentre.py" \
           "api/unit_mambuuser.py" \
           "api/unit_mambuproduct.py" \
           "api/unit_mambutask.py" \
           "api/unit_mambutransaction.py" \
      )
for test in ${tests[@]}
do
    test_prefix=`cut -c 1-3 <<< $test`
    [ $apiv2 != "apiv2" ] && [ $test_prefix == "api" ] && continue
    echo $test
    coverage run --append --rcfile=./.coveragerc tests/$test
    out=$?
    if [ $out -ne 0 ];then
        fails=$(( fails+1 ))
    fi
    echo ""
done

if [ $fails -ne 0 ];then
    exit 1
else
    coverage report --precision=2
fi
