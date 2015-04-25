OUTFILE=sly-addon.zip

all: build zip

build:
	mkdir -p build/modules
	cp -r sly build/modules
	cp -r deps/ build/modules

# Exclude compiled .pyc files from the zip.
zip: build
	cd build && find . \! -name "*.pyc" -print | zip $(OUTFILE) -@

clean:
	rm -rf build/

.PHONY: all build zip