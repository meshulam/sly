OUTFILE=sly-addon.zip

all: prepare deps zip

prepare:
	mkdir -p build/modules
	cp -r sly build/modules

deps: prepare
	cp -r deps/ build/modules

zip: prepare
	cd build && find . \! -name "*.pyc" -print | zip $(OUTFILE) -@

clean:
	rm -rf build/

.PHONY: all prepare deps zip