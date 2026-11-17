# Run on the Comet (or push first with `make push`).
LABEL ?= mesa-new
RUN   ?= $(shell date +%Y%m%d)_$(LABEL)
COMET ?= mecha@comet.local

list:        ## show the tests that would run
	python3 scripts/gpuval.py run --list
sysinfo:     ## capture hardware/driver facts only
	python3 scripts/gpuval.py sysinfo
run:         ## all tests, risky ones last; re-run with same RUN to resume
	python3 -u scripts/gpuval.py run --label $(LABEL) --run-id $(RUN)
run-safe:    ## everything except the tests known to reset the board
	python3 -u scripts/gpuval.py run --label $(LABEL) --run-id $(RUN) --skip-risky
report:      ## make REPORT.md (BASE=<run-id> to compare)
	python3 scripts/gpuval.py report $(RUN) $(BASE)
push:        ## laptop -> Comet
	git rev-parse --short HEAD > .revision 2>/dev/null || true
	rsync -a --exclude runs/ --exclude .git --exclude cases/ --exclude app-benchmarks/ --exclude baseline-fedora-mesa-26.2.6/ --exclude chromium-nv12-mr46144/ --exclude gtk4-apps-mr46144-2026-11-17/ --exclude environment/ ./ $(COMET):gpu-test/
pull:        ## Comet -> laptop (raw logs included)
	rsync -a $(COMET):gpu-test/runs/ runs/
