#!/bin/bash

# How many cores can we use
CORES=4


gzip -d lambda_virus.200bp.50x.1percentError.fa.gz

rm -rf testFixedK/ testNtcard/



# Start Bcool withoyt ntcard
../Bcool.py  -u lambda_virus.200bp.50x.1percentError.fa -k 61  -o testFixedK -t $CORES

printf "\n\n\n"
# Start Bcool with ntcard
# Test ok?
if [ -f "testFixedK/reads_corrected.fa" ];
then
  echo "IT WORKS without ntcard !";
else
   echo "FAIL the install wen wrong"
fi
printf "\n\n\n"

../Bcool.py  -u lambda_virus.200bp.50x.1percentError.fa  -o testNtcard -t $CORES

printf "\n\n\n"

if [ -f "testNtcard/reads_corrected.fa" ];
then
  echo "IT WORKS with ntcard!";
else
   echo "FAIL ntcard install went wrong"
fi

printf "\n\n\n"
