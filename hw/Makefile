GSCH2PCB = gsch2pcb
DJBOXSYM = djboxsym

PROJ = bus_m4gyk_II.prj
SYMBOLS = CY7C68013A.sym \
	5M570ZT100.sym \
	LD1117A.sym \
	MCP1700.sym \
	MCP1826.sym

SCH = bus_m4gyk_II.sch \
	power.sch \
	conf.sch

PCB = bus_m4gyk_II.pcb


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
