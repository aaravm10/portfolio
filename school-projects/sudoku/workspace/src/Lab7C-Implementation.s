// uint32_t GetNibble(void *nibbles, uint32_t which);

		.syntax		unified
		.cpu		cortex-m4
		.text
	
		.global		GetNibble
		.thumb_func
		.align
GetNibble:
	MOV	R2,R1
	LSR	R2,R2,#1
	LDRB	R2,[R0,R2]
	AND	R3,R1,1
	CMP 	R3,1
	BNE	exit
	LSR	R2,R2,#4
exit:
	AND	R0,R2,0xF
	BX	LR


// void PutNibble(void *nibbles, uint32_t which, uint32_t value);

		.global		PutNibble
		.thumb_func
		.align
PutNibble:
	MOV	R3,R1
        AND     R2, R2, 0xff
	LSR	R3,R3,#1
	ADD	R12,R0,R3	
	LDRB	R3,[R12]
	AND	R1,R1,1
	CMP	R1,1
	BNE	else
	AND	R3,R3,0xF
        LSL     R2, R2, 4
	ORR	R3,R3,R2
	B 	exit1
else:
	AND	R3,R3,0xF0
	ORR	R3,R3,R2
exit1:
	STRB	R3,[R12]
	BX	LR
	
	.end
