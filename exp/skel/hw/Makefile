GSCH2PCB = gsch2pcb
DJBOXSYM = djboxsym

PROJ = skel.prj
SYMBOLS =

SCH = skel.sch \

PCB = skel.pcb


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
