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
	int col_range;
	double temp;
	int r_extra;
	int c_extra;
	int curr_r_start;
	int curr_c_start;
	int next_start;
	int next_row;
	int r_threads;
	int c_threads;
	double start;
	double end;
	int tc;
	int extra_threads;
	int flip;
	

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

	temp = sqrt((double)ThreadCount);
	r_threads = temp;
	c_threads = temp;
	if(r_threads == 0) {
		r_threads = 1;
		c_threads = 1;
	} else { /* handle round off */
		tc = r_threads * c_threads;
		extra_threads = ThreadCount - tc;
		flip = 0;
		/*
		 * distribute extra threads evenly among row threads and col
		 * threads
		 */
		while(extra_threads > 0) {
			if(flip == 0) {
				r_threads++;
			} else {
				c_threads++;
			}
			flip = 1 - flip;
			extra_threads--;
		}
	}

	row_range = a->ydim / r_threads;
	r_extra = a->ydim % r_threads;

	col_range = b->xdim / c_threads;
	c_extra = b->xdim % c_threads;

	if(row_range == 0) {
		fprintf(stderr,"more row threads (%d) than rows in A matrix (%d)\n",
			a->ydim,
			r_threads);
		fprintf(stderr,"setting thread count to %d\n",
				a->ydim);
		row_range = 1;
		r_threads = a->ydim;
		r_extra = 0;
	}

	if(col_range == 0) {
		fprintf(stderr,"more col threads (%d) than cols in B matrix (%d)\n",
			b->xdim,
			c_threads);
		fprintf(stderr,"setting thread count to %d\n",
				a->ydim);
		col_range = 1;
		c_threads = b->xdim;
		c_extra = 0;
	}

	tids = (pthread_t *)malloc(r_threads*c_threads*sizeof(MM_arg));
	if(tids == NULL) {
		fprintf(stderr,"no space for thread ids\n");
		exit(1);
	}

	mms = (MM_arg *)malloc(r_threads*c_threads*sizeof(MM_arg));
	if(mms == NULL) {
		fprintf(stderr,"no space for mm thread args\n");
		exit(1);
	}

	/*
	 * partition rectangles
	 */
	start = CTimer();
	curr_r_start = 0;
	for(i=0; i < r_threads; i++) {
		next_start = curr_r_start;
		next_row = row_range;
		curr_r_start += row_range;
		if(r_extra > 0) {
			next_row += 1;
			curr_r_start += 1;
			r_extra--;
		}
		curr_c_start = 0;
		c_extra = b->xdim % c_threads;
		for(j=0; j < c_threads; j++) {
			mms[i*c_threads+j].id = i*c_threads+j;
			mms[i*c_threads+j].starting_row = next_start;
			mms[i*c_threads+j].row_range = next_row;
			mms[i*c_threads+j].starting_col = curr_c_start;
			mms[i*c_threads+j].col_range = col_range;
			curr_c_start += col_range;
			if(c_extra > 0) {
				mms[i*c_threads+j].col_range += 1;
				curr_c_start += 1;
				c_extra--;
			}
			mms[i*c_threads+j].a = a;
			mms[i*c_threads+j].b = b;
			mms[i*c_threads+j].c = C;
			err = pthread_create(&tids[i*c_threads+j],NULL,
				MMThread,&mms[i*c_threads+j]);
			if(err != 0) {
				fprintf(stderr,"thread create for thread %d failed\n",
					i*c_threads+j);
				exit(1);
			}
		}
	}

	for(i=0; i < r_threads; i++) {
		for(j=0; j < c_threads; j++) {
			err = pthread_join(tids[i*c_threads+j],&result);
			if(result != NULL) {
				fprintf(stderr,
			"thread %d failed to complete its subregion\n",i*c_threads+j);
				exit(1);
			}
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

	

	



