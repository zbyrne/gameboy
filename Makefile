test: test_z80

test_z80:
	gcc -o z80/test_z80.out z80/test_z80.c -lcheck
	z80/test_z80.out

clean: clean_z80

clean_z80:
	-rm z80/*.out
