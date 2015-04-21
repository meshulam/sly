
deps:
	cd deps && zip -r ../sly-addon.zip .

addon:
	zip -r sly-addon.zip sly/

addon-test:
	cd addon && zip -r ../sly-addon.zip ohai.py modules


.PHONY: deps addon addon-zip