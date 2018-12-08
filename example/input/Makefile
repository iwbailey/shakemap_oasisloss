
# List of the binary files we need in this folder
obj = coverages.bin \
	items.bin \
	events.bin \
	gulsummaryxref.bin

all: $(obj)

# Conversion from csv for each file
coverages.bin: coverages.csv
	coveragetobin < $< > $@

items.bin: items.csv
	itemtobin < $< > $@

events.bin: events.csv
	evetobin < $< > $@

gulsummaryxref.bin: gulsummaryxref.csv
	gulsummaryxreftobin < $< > $@

# Delete the binary files so we can start again
clean:
	rm -f $(obj)
