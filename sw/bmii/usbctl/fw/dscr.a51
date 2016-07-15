.module DEV_DSCR

; descriptor types
DSCR_DEVICE_TYPE=1
DSCR_CONFIG_TYPE=2
DSCR_STRING_TYPE=3
DSCR_INTERFACE_TYPE=4
DSCR_ENDPOINT_TYPE=5
DSCR_DEVQUAL_TYPE=6

; for the repeating interfaces
DSCR_INTERFACE_LEN=9
DSCR_ENDPOINT_LEN=7

; endpoint types
ENDPOINT_TYPE_CONTROL=0
ENDPOINT_TYPE_ISO=1
ENDPOINT_TYPE_BULK=2
ENDPOINT_TYPE_INT=3

.globl _dev_dscr, _dev_qual_dscr, _highspd_dscr, _dev_strings

.area DSCR_AREA		(CODE)

_dev_dscr:
	.db	dev_dscr_end-_dev_dscr		; len
	.db	DSCR_DEVICE_TYPE		; type
	.dw	0x0002				; usb 2.0
	.db	0xff  				; class (vendor specific)
	.db	0xff				; subclass (vendor specific)
	.db	0xff				; protocol (vendor specific)
	.db	64				; packet size (ep0)
	.dw	0xFFFF				; vendor id 
	.dw	0xFEEB				; product id
	.dw	0x0100				; version id
	.db	1				; manufacture str idx
	.db	2				; product str idx
	.db	0				; serial str idx 
	.db	1				; n configurations
dev_dscr_end:

_dev_qual_dscr:
	.db	dev_qualdscr_end-_dev_qual_dscr
	.db	DSCR_DEVQUAL_TYPE
	.dw	0x0002				; usb 2.0
	.db	0xff
	.db	0xff
	.db	0xff
	.db	512
	.db	1				; n configs
	.db	0				; extra reserved byte
dev_qualdscr_end:

_highspd_dscr:
	.db	highspd_dscr_end-_highspd_dscr
	.db	DSCR_CONFIG_TYPE
	.db	(highspd_dscr_realend-_highspd_dscr) % 256
	.db	(highspd_dscr_realend-_highspd_dscr) / 256
	.db	1		; n interfaces
	.db	1		; config number
	.db	3		; config string
	.db	0x80		; attrs = bus powered, no wakeup
	.db	0x32		; max power = 100ma
highspd_dscr_end:

	.db	DSCR_INTERFACE_LEN
	.db	DSCR_INTERFACE_TYPE
	.db	0			; index
	.db	0			; alt setting idx
	.db	2			; n endpoints
	.db	0xff			; class
	.db	0xff
	.db	0xff
	.db	3			; string index

; endpoint 2 out
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x02			; ep2 dir=OUT and address
	.db	ENDPOINT_TYPE_BULK	; type
	.db	0x00			; max packet LSB
	.db	0x02			; max packet size=512 bytes
	.db	0x00			; polling interval

; endpoint 6 in
	.db	DSCR_ENDPOINT_LEN
	.db	DSCR_ENDPOINT_TYPE
	.db	0x86			; ep6 dir=IN and address
	.db	ENDPOINT_TYPE_BULK	; type
	.db	0x00			; max packet LSB
	.db	0x02			; max packet size=512 bytes
	.db	0x00			; polling interval

highspd_dscr_realend:

.even
_dev_strings:

_string1:
	.db string1end-_string1
	.db DSCR_STRING_TYPE
	.ascii 'L'
	.db 0
	.ascii 'S'
	.db 0
	.ascii 'E'
	.db 0
string1end:

_string2:
	.db string2end-_string2
	.db DSCR_STRING_TYPE
	.ascii 'B'
	.db 0
	.ascii 'U'
	.db 0
	.ascii 'S'
	.db 0
	.ascii '_'
	.db 0
	.ascii 'M'
	.db 0
	.ascii '4'
	.db 0
	.ascii 'G'
	.db 0
	.ascii 'Y'
	.db 0
	.ascii 'K'
	.db 0
	.ascii '_'
	.db 0
	.ascii 'I'
	.db 0
	.ascii 'I'
	.db 0
string2end:

_string3:
	.db string3end-_string3
	.db DSCR_STRING_TYPE
	.ascii 'b'
	.db 0
	.ascii 'm'
	.db 0
	.ascii 'i'
	.db 0
	.ascii 'i'
	.db 0
string3end:

_dev_strings_end:
	.dw 0x0000
