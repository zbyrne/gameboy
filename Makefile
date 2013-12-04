z80.o:
	gcc -o z80/z80.o -c z80/z80.c

test: test_z80

test_z80: z80.o
	gcc -o z80/test_z80.out z80/test_z80.c z80/z80.o -lcheck
	z80/test_z80.out

clean: clean_z80

clean_z80:
	-rm z80/*.o z80/*.out
