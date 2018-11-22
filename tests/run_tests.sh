#!/bin/bash

# Test we can set up an areaperil grid and assign coordinates to it
python3 test_areaperilgrid.py

# Test we can assign intensities to a set of intensity bins
python3 test_assignintensities.py

# Test we can assign intensity uncertainty to probabilty bins
python3 test_intensuncert.py

# Test we can create a damage bin dict for oasis
python3 test_damagebindict.py

# Test we can create an oasis footprint file from a shakemap
python3 test_footprint.py

# Test we can create a damage function from a fragility curve
python3 test_damagefunction.py
