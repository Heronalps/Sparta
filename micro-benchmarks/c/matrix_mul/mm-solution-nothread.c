#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "array.h"
#include "read-matrix.h"
#include "matrix-multiply.h"
#include "c-timer.h"

#define ARGS "a:b:"
char *Usage = "mm-solution-nothread -a a-matrix-file -b b-matrix-file\n";

char Afile[8192];
char Bfile[8192];


int main(int argc, char *argv[])
{
	int c;
	int i;
	int j;
	Array2D *a;
	Array2D *b;
	Array2D *C;
	int err;
	double start;
	double end;

	while((c = getopt(argc,argv,ARGS)) != EOF) {
		switch(c) {
			case 'a':
				strncpy(Afile,optarg,sizeof(Afile));
				break;
			case 'b':
				strncpy(Bfile,optarg,sizeof(Bfile));
				break;
			default:
				fprintf(stderr,"unrecognized command %c\n",
					(char)c);
				fprintf(stderr,"usage: %s",Usage);
				exit(1);
		}
	}

	if(Afile[0] == 0) {
		fprintf(stderr,"must specify an A matrix file\n");
		fprintf(stderr,"usage: %s",Usage);
		exit(1);
	}

	if(Bfile[0] == 0) {
		fprintf(stderr,"must specify an B matrix file\n");
		fprintf(stderr,"usage: %s",Usage);
		exit(1);
	}

	a = ReadMatrix(Afile);
	if(a == NULL) {
		fprintf(stderr,"couldn't successfully read and parse file %s\n",Afile);
		exit(1);
	}

	b = ReadMatrix(Bfile);
	if(b == NULL) {
		fprintf(stderr,"couldn't successfully read and parse file %s\n",Bfile);
		exit(1);
	}

	C = MakeArray2D(a->ydim,b->xdim);
	if(C == NULL) {
		fprintf(stderr,"couldn't allocate space for C array\n");
		exit(1);
	}

	start = CTimer();
	for (int i = 0; i < 1; i++) {
		err = MultiplyArray2D(a,b,C);
	}
	end = CTimer();

	if(err < 0)
	{
		printf("matrix multiply failed\n");
		exit(1);
	}
		
	// printf("c:\n");
	// PrintMatrix(C);

	FreeArray2D(a);
	FreeArray2D(b);
	FreeArray2D(C);

	printf("%f seconds\n",end-start);

	return(0);
}

	

	



