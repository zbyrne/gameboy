z80.o:
	gcc -o z80/z80.o -c z80/z80.c

test: test_z80

test_z80: test_z80_ld test_z80_inc test_z80_dec test_z80_rot

test_z80_ld: z80.o
	gcc -o z80/test_z80_ld.out z80/test_z80_ld.c z80/z80.o -lcheck
	z80/test_z80_ld.out

test_z80_inc: z80.o
	gcc -o z80/test_z80_inc.out z80/test_z80_inc.c z80/z80.o -lcheck
	z80/test_z80_inc.out

test_z80_dec: z80.o
	gcc -o z80/test_z80_dec.out z80/test_z80_dec.c z80/z80.o -lcheck
	z80/test_z80_dec.out

test_z80_rot: z80.o
	gcc -o z80/test_z80_rot.out z80/test_z80_rot.c z80/z80.o -lcheck
	z80/test_z80_rot.out

clean: clean_z80

clean_z80:
	-rm z80/*.o z80/*.out
