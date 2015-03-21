z80.o:
	gcc -o z80.o -c z80.c

test: test_z80_ld test_z80_inc test_z80_dec test_z80_rot

test_z80_ld: z80.o
	gcc -o test_z80_ld.out test_z80_ld.c z80.o
	./test_z80_ld.out

test_z80_inc: z80.o
	gcc -o test_z80_inc.out test_z80_inc.c z80.o
	./test_z80_inc.out

test_z80_dec: z80.o
	gcc -o test_z80_dec.out test_z80_dec.c z80.o
	./test_z80_dec.out

test_z80_rot: z80.o
	gcc -o test_z80_rot.out test_z80_rot.c z80.o
	./test_z80_rot.out

clean:
	-rm *.o *.out
