CXX := clang++
CXXFLAGS := -std=c++11

.PHONY: all
all: z80.o
	ls .