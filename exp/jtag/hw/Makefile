GSCH2PCB = gsch2pcb
DJBOXSYM = djboxsym

PROJ = bmii_jtag.prj
SYMBOLS = SN74AVC4T245.sym \
    CON351779862.sym

SCH = bmii_jtag.sch \

PCB = bmii_skel.pcb


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
