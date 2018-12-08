
# Get the number of intensity bins from the bin dictionary
nBins = $(shell wc -l intensity_bin_dict.csv | gawk '{print($$1-1)}')

# Get the number of damage bins from the bin dictionary
nDmgBins = $(shell wc -l damage_bin_dict.csv | gawk '{print($$1-1)}')

# List the binary files we want in this folder
obj = footprint.bin damage_bin_dict.bin vulnerability.bin random.bin

all: $(obj)

# Convert from csv for each target
footprint.bin: footprint.csv intensity_bin_dict.csv
	footprinttobin -i ${nBins} -n < $<

damage_bin_dict.bin: damage_bin_dict.csv
	damagebintobin < $< > $@

vulnerability.bin: vulnerability.csv damage_bin_dict.csv
	vulnerabilitytobin -d ${nDmgBins} < $< > $@

random.bin: random.csv
	randtobin < $< > $@

# Remove binary files so we can start again
clean:
	rm -f $(obj)
