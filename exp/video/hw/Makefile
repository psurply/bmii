GSCH2PCB = gsch2pcb
DJBOXSYM = djboxsym

PROJ = video.prj
SYMBOLS = AS6C1008.sym

SCH = video.sch

PCB = video.pcb


SYMBOLS := $(addprefix symbols/, $(SYMBOLS))
SCH := $(addprefix sch/, $(SCH))
PCB := $(addprefix pcb/, $(PCB))

.PHONY: all bom

all: $(SYMBOLS) $(PCB)

bom: bom.csv

bom.dsv: $(SCH)
	gnetlist -g bom2 -o $@ -Oattribs=device,value,footprint,url $(SCH)

%.csv: %.dsv
	sed 's_:\([^/]\)_;\1_g' $< > $@

%.sym: %.symdef
	$(DJBOXSYM) $< > $@

%.pcb: $(SCH)
	$(GSCH2PCB) $(PROJ)
