CXX := clang++
CXXFLAGS := -std=c++11

test_%.out: test_%.cc %.o
	$(CXX) $(CXXFLAGS) -o $@ $^
	./$@
