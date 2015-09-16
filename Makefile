CFLAGS += -Wall -Wextra -O3 -lm -fopenmp

mi : mi.c
	gcc ${CFLAGS} -o $@ $^

clean:
	rm -f mi
