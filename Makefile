CFLAGS += -Wall -Wextra -O3 -lm -fopenmp

GAMES := rm2 duckhunt smb tecmo ducktales battletoads smb3 tloz doubledragon

mi : mi.c
	gcc ${CFLAGS} -o $@ $^

clean:
	rm -f mi
