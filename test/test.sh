#!/bin/bash

# How many cores can we use
CORES=4



rm -rf testFixedK/ testNtcard/



# Start Bcool withoyt ntcard
../Bcool  -u lambda_virus.200bp.50x.1percentError.fa.gz -k 61  -o testFixedK -t $CORES

printf "\n\n\n"
# Start Bcool with ntcard
# Test ok?
if [ -f "testFixedK/reads_corrected.fa" ];
then
  echo "IT WORKS without ntcard !";
else
   echo "FAIL the install went wrong"
fi
printf "\n\n\n"

../Bcool  -u lambda_virus.200bp.50x.1percentError.fa  -o testNtcard -t $CORES

printf "\n\n\n"

if [ -f "testNtcard/reads_corrected.fa" ];
then
  echo "IT WORKS with ntcard!";
else
   echo "FAIL ntcard install went wrong"
fi

printf "\n\n\n"
