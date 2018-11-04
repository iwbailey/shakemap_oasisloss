shakemap_oasisloss
==================

Estimate loss for a set of locations based on a shakemap footprint

## Install locally
pip install --user -e .


## Requirements for getting an oasis loss estimate

### Static tables

#### Damage bin definition file
Define the granularity of damage ratios (between 0 and 1) used in the model

TODO: what are the table fields?

TODO: what is the file name and where does it need to be stored?

#### Footprint file
Defines the intensity distribution per location

Table with event\_id, area\_peril\_id, intensity\_bin\_id, prob.

TODO: check if prob needs to sum to 1 for each area\_peril\_id.

##### Requirements
- Intensity bin definition
- Area peril locations

##### Options
- Option 1: Mean intensity only

-- Define the areaperil grid
-- Read in the shakemap
-- Assign shakemap grid locations to areaperil locations
-- Filter out intensities lower than any intensity bins
-- * TODO: Assign mean intensities to appropriate intensity bin
-- TODO: Write out the csv file


- Option 2: With intra-event uncertainty

-- * TODO: For each area peril grid, use the mean and std calculate the probability in each intenity bin

--

- Option 3: TOOD: multiple footprint files for correlated intra-event

##### Vulnerability file


### Other tables
