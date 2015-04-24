OUTFILE=sly-addon.zip

default: prepare deps zip

prepare:
	mkdir -p build
	cp -r sly build/

deps: prepare

zip: prepare
	cd build && zip -r ../$(OUTFILE) .


.PHONY: prepare deps zip