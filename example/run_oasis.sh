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
ofile=./results/loclosses.csv

eve $processNum $numProcesses | \
    getmodel | \
    gulcalc -r -S$numSamples -c - | \
    summarycalc -g -$summarygrpid - | \
    eltcalc > $ofile
echo "Written to ${ofile}"


# Summary calc gives the event loss distribution for all locations
echo "Calculating event loss sample distribution..."

summarygrpid=2
ofile=./results/eventloss_summary.csv

eve $processNum $numProcesses | \
    getmodel | \
    gulcalc -r -S$numSamples -c - | \
    summarycalc -g -$summarygrpid - | \
    summarycalctocsv > $ofile
echo "Written to ${ofile}"
