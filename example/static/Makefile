
nBins = `wc -l intensity_bin_dict.csv | gawk '{print($$1-1)}'`

nDmgBins = `wc -l damage_bin_dict.csv | gawk '{print($$1-1)}'`

footprint.bin: footprint.csv
	footprinttobin -i ${nBins} -n < $<

damage_bin_dict.bin: damage_bin_dict.csv
	damagebintobin < $< > $@

vulnerability.bin: vulnerability.csv
	vulnerabilitytobin -d ${nDmgBins} < $< > $@

all: footprint.bin damage_bin_dict.bin vulnerability.bin

clean:
	rm footprint.bin
	rm footprint.idx
	rm damage_bin_dict.bin
	rm vulnerability.bin
