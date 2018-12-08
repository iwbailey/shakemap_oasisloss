#!/bin/bash
# Generate the oasis outputs

numSamples=${1-100}
numRand=${2-100000}
randSeed=12345
processNum=1
numProcesses=1

# Make sure the inputs are up to date
make -C static/
make -C input/

# Event loss table which gives the estimated loss per location
echo "Calculating loss per location..."

summarygrpid=1
ofile=./results/loccdf.csv

eve $processNum $numProcesses | \
    getmodel | \
    cdftocsv > $ofile
echo "Written to ${ofile}"
