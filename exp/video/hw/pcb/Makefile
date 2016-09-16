PROJ = video
PCB = $(PROJ).pcb
PNG = $(PROJ).png
GERBS = $(PROJ).zip
GERB_FILES = \
	      $(PROJ).GKO \
	      $(PROJ).TXT \
	      $(PROJ).GTO \
	      $(PROJ).GTS \
	      $(PROJ).GTL \
	      $(PROJ).GBL \
	      $(PROJ).GBS \
	      $(PROJ).GBO

all:: $(GERBS) $(PNG)

png:: $(PNG)
	feh $<

%.zip: $(GERB_FILES)
	zip $@ $^

%.GTL: %.top.gbr
	cp $< $@

%.GBL: %.bottom.gbr
	cp $< $@

%.GTS: %.topmask.gbr
	cp $< $@

%.GBS: %.bottommask.gbr
	cp $< $@

%.GTO: %.topsilk.gbr
	cp $< $@

%.GBO: %.bottomsilk.gbr
	cp $< $@

%.TXT: %.plated-drill.cnc
	cp $< $@

%.GKO: %.outline.gbr
	cp $< $@

%.gbr %.cnc: $(PCB)
	pcb -x gerber --gerberfile $(PROJ) --metric --all-layers $<

%.png: $(PCB)
	pcb -x png --outfile $@ --dpi 300 --photo-mode --only-visible \
	    --use-alpha $<

clean::
	$(RM) *.gbr *.cnc $(GERB_FILES) $(GERBS)

gerbv:: $(GERB_FILES)
	gerbv $^
