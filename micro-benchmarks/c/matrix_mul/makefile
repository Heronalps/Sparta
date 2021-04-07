CC=gcc
CFLAGS=-g

all: print-rand-matrix read-matrix matrix-multiply-test matrix-multiply-thread-test mm-solution-nothread mm-solution mm-solution-square mmult

mmult: mmult.c c-timer.o c-timer.h
	${CC} ${CFLAGS} -o mmult mmult.c c-timer.o -lpthread -lm

matrix-multiply-test: matrix-multiply.c array.h array.o
	${CC} ${CFLAGS} -DSTANDALONE -o matrix-multiply-test matrix-multiply.c array.o

matrix-multiply-thread-test: matrix-multiply-thread.c array.h array.o
	${CC} ${CFLAGS} -DSTANDALONE -o matrix-multiply-thread-test matrix-multiply-thread.c array.o -lpthread

mm-solution-nothread: mm-solution-nothread.c array.h array.o read-matrix.h read-matrix.o matrix-multiply.o c-timer.h c-timer.o
	${CC} ${CFLAGS} -o mm-solution-nothread mm-solution-nothread.c array.o read-matrix.o matrix-multiply.o c-timer.o -lpthread

mm-solution: mm-solution.c array.h array.o read-matrix.h read-matrix.o matrix-multiply-thread.o c-timer.o c-timer.h
	${CC} ${CFLAGS} -o mm-solution mm-solution.c array.o read-matrix.o matrix-multiply-thread.o c-timer.o -lpthread

mm-solution-square: mm-solution-square.c array.h array.o read-matrix.h read-matrix.o matrix-multiply-thread.o c-timer.o c-timer.h
	${CC} ${CFLAGS} -o mm-solution-square mm-solution-square.c array.o read-matrix.o matrix-multiply-thread.o c-timer.o -lpthread -lm

print-rand-matrix: print-rand-matrix.c
	${CC} ${CFLAGS} -o print-rand-matrix print-rand-matrix.c

read-matrix: read-matrix.c array.h array.o
	${CC} ${CFLAGS} -DSTANDALONE -o read-matrix read-matrix.c array.o

read-matrix.o: read-matrix.c array.h
	${CC} ${CFLAGS} -c read-matrix.c

array.o: array.c array.h
	${CC} ${CFLAGS} -c array.c

c-timer.o: c-timer.c c-timer.h
	${CC} ${CFLAGS} -c c-timer.c

matrix-multiply.o: matrix-multiply.c matrix-multiply.h array.h
	${CC} ${CFLAGS} -c matrix-multiply.c

matrix-multiply-thread.o: matrix-multiply-thread.c matrix-multiply-thread.h array.h
	${CC} ${CFLAGS} -c matrix-multiply-thread.c

clean:
	rm *.o print-rand-matrix read-matrix matrix-multiply-test matrix-multiply-thread-test mm-solution mm-solution-nothread mm-solution-square mmult 
	rm -rf *.dSYM *.txt

run:
	./print-rand-matrix -r 512 -c 512 > m1.txt
	./print-rand-matrix -r 512 -c 512 > m2.txt
	./mm-solution-nothread -a m1.txt -b m2.txt
