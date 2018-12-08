
# Get the number of intensity bins from the bin dictionary
nBins = $(shell wc -l intensity_bin_dict.csv | gawk '{print($$1-1)}')

# Get the number of damage bins from the bin dictionary
nDmgBins = $(shell wc -l damage_bin_dict.csv | gawk '{print($$1-1)}')

# Get the minimum prob
fpflag = $(shell gawk 'BEGIN{FS=","; minp=1.0;}{if(NR>1 && $$4<minp && $$4>0) minp=$$4;}END{if(minp>0.999)print("-n")}' footprint.csv)


# List the binary files we want in this folder
obj = footprint.bin damage_bin_dict.bin vulnerability.bin random.bin

all: $(obj)

# Convert from csv for each target
footprint.bin: footprint.csv intensity_bin_dict.csv
	footprinttobin -i ${nBins} ${fpflag} < $<

damage_bin_dict.bin: damage_bin_dict.csv
	damagebintobin < $< > $@

vulnerability.bin: vulnerability.csv damage_bin_dict.csv
	vulnerabilitytobin -d ${nDmgBins} < $< > $@

random.bin: random.csv
	randtobin < $< > $@

# Remove binary files so we can start again
clean:
	rm -f $(obj)
