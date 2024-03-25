linelength = 110
files = src/nifti2gif/*.py

pretty:
	isort $(files)
	black --line-length $(linelength) $(files)

test_pretty:
	isort --check --profile black $(files)
	black --line-length $(linelength) --check $(files)

test:
	$(call test_pretty)
	flake8 --max-line-length $(linelength) $(files)