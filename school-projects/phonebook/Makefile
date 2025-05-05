all: lab10

CC = gcc
CFLAGS = -g

SRCS = main.c list.c file.c 
HEADERS = lab10.h 

lab10: $(SRCS) $(HEADERS)
	$(CC) $(CFLAGS) $(SRCS) -o "$@" -lpthread

lab10i-debug: $(SRCS) $(HEADERS)
	$(CC) $(CFLAGS) -O0 $(SRCS) -o "$@"  -lpthread

clean:
	rm -f lab10 lab10-debug
