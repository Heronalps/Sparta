#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <pthread.h>

#include "array.h"
#include "read-matrix.h"
#include "matrix-multiply-thread.h"
#include "c-timer.h"

#define ARGS "a:b:t:"
char *Usage = "mm-solution -a a-matrix-file -b b-matrix-file -t thread_count\n";

char Afile[4096];
char Bfile[4096];
int ThreadCount;


int main(int argc, char *argv[])
{
	int c;
	int i;
	int j;
	Array2D *a;
	Array2D *b;
	Array2D *C;
	int err;
	pthread_t *tids;
	MM_arg *mms;
	void *result;
	int row_range;
	double temp;
	int extra;
	int curr_start;
	double start;
	double end;
	

	ThreadCount = 1;

	while((c = getopt(argc,argv,ARGS)) != EOF) {
		switch(c) {
			case 'a':
				strncpy(Afile,optarg,sizeof(Afile));
				break;
			case 'b':
				strncpy(Bfile,optarg,sizeof(Bfile));
				break;
			case 't':
				ThreadCount = atoi(optarg);
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

	if(ThreadCount <= 0) {
		fprintf(stderr,"must specify thread count as a positive number\n");
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

	row_range = a->ydim / ThreadCount;
	extra = a->ydim % ThreadCount;

	if(row_range == 0) {
		fprintf(stderr,"more threads (%d) than rows in A matrix (%d)\n",
			a->ydim,
			ThreadCount);
		fprintf(stderr,"setting thread count to %d\n",
				a->ydim);
		row_range = 1;
		ThreadCount = a->ydim;
		extra = 0;
	}

	tids = (pthread_t *)malloc(ThreadCount*sizeof(MM_arg));
	if(tids == NULL) {
		fprintf(stderr,"no space for thread ids\n");
		exit(1);
	}

	mms = (MM_arg *)malloc(ThreadCount*sizeof(MM_arg));
	if(mms == NULL) {
		fprintf(stderr,"no space for mm thread args\n");
		exit(1);
	}

	/*
	 * only partitions along the row dimension of the A matrix
	 */
	start = CTimer();
	curr_start = 0;
	for(i=0; i < ThreadCount; i++) {
		mms[i].id = i;
		mms[i].starting_row = curr_start;
		mms[i].row_range = row_range;
		curr_start += row_range;
		if(extra > 0) {
			mms[i].row_range += 1;
			curr_start += 1;
			extra--;
		}
		mms[i].starting_col = 0;
		mms[i].col_range = b->xdim;
		mms[i].a = a;
		mms[i].b = b;
		mms[i].c = C;
		err = pthread_create(&tids[i],NULL,
			MMThread,&mms[i]);
		if(err != 0) {
			fprintf(stderr,"thread create for thread %d failed\n",
				i);
			exit(1);
		}
	}

	for(i=0; i < ThreadCount; i++) {
		err = pthread_join(tids[i],&result);
		if(result != NULL) {
			fprintf(stderr,
				"thread %d failed to complete its subregion\n",i);
			exit(1);
		}
	}
	end = CTimer();
	printf("c:\n");
	PrintMatrix(C);

	FreeArray2D(a);
	FreeArray2D(b);
	FreeArray2D(C);

	free(tids);
	free(mms);

	printf("%f seconds\n",end-start);

	return(0);
}

	

	



