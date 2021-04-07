#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <pthread.h>

#include "array.h"
#include "matrix-multiply-thread.h"


/*
 * computes c = a * b
 *
 * where rows and cols specified by starting and ranges is in the c array
 */
void *MMThread(void *arg)
{
	int i;
	int j;
	int k;
	double acc;
	int new_r;
	int new_c;
	Array2D *a; 
	Array2D *b;
	Array2D *c;
	int starting_row;
	int row_range;
	int starting_col;
	int col_range;
	MM_arg *mm;
	double *data;
	int end_r;
	int end_c;

	mm = (MM_arg *)arg;
	a = mm->a;
	b = mm->b;
	c = mm->c;
	starting_row = mm->starting_row;
	starting_col = mm->starting_col;
	row_range = mm->row_range;
	col_range = mm->col_range;


	if(a->xdim != b->ydim)
	{
		return((void *)-1);
	}

	new_r = a->ydim;
	new_c = b->xdim;

	if(c->ydim != new_r) {
		return((void *)-1);
	}

	if(c->xdim != new_c) {
		return((void *)-1);
	}

	data = c->data;
	end_r = starting_row + row_range;
	end_c = starting_col + col_range;

	if(end_r > new_r) {
#ifdef VERBOSE
		fprintf(stderr,"thread %d end_r %d, new_r %d\n",
			mm->id,
			end_r,
			new_r);
#endif
		return((void *)-1);
	}
	if(end_c > new_c) {
#ifdef VERBOSE
		fprintf(stderr,"thread %d end_c %d, new_c %d\n",
			mm->id,
			end_c,
			new_c);
#endif
		return((void *)-1);
	}

	for(i=starting_row; i < end_r; i++)
	{
		for(j=starting_col; j < end_c; j++)
		{
			acc = 0.0;
			for(k=0; k < a->xdim; k++)
			{
				acc += (a->data[i*(a->xdim)+k] *
					b->data[k*(b->xdim)+j]);
			}
			data[i*new_c+j] = acc;
#ifdef VERBOSE
			printf("thread: %d computed (%d,%d)\n",mm->id,i,j);
#endif
		}
	}

	return(NULL);
}

#ifdef STANDALONE

int main(int argc, char *argv[])
{
	int i;
	int j;
	Array2D *a;
	Array2D *b;
	Array2D *c;
	pthread_t tids[2];
	MM_arg mms[2];
	int err;
	void *ret;

	a = MakeArray2D(3,5);
	b = MakeArray2D(5,3);

	for(i=0; i < 3; i++)
	{
		for(j=0; j < 5; j++)
		{
			a->data[i*a->xdim+j] = 3.0;
			b->data[j*b->xdim+i] = 5.0;
		}
	}

	c = MakeArray2D(3,3);

	for(i=0; i < 2; i++) {
		mms[i].a = a;
		mms[i].b = b;
		mms[i].c = c;
		if(i == 0) {
			mms[i].starting_row = 0;
			mms[i].row_range = 3;
			mms[i].starting_col = 0;
			mms[i].col_range = 1;
		} else {
			mms[i].starting_row = 0;
			mms[i].row_range = 3;
			mms[i].starting_col = 1;
			mms[i].col_range = 2;
		}
		mms[i].id = i;
		err = pthread_create(&tids[i],NULL,MMThread,(void *)&mms[i]);
		if(err != 0) {
			fprintf(stderr,"create failed for thread %d\n",i);
			exit(1);
		}
	}

	for(i=0; i < 2; i++) {
		err = pthread_join(tids[i],&ret);
		if(err != 0) {
			fprintf(stderr,"join failed for thread %d\n",i);
			exit(1);
		}
		if(ret != NULL) {
			fprintf(stderr,"thread %d threw an error\n",i);
			exit(1);
		}
	}

	printf("a:\n");
	PrintArray2D(a);
	printf("b:\n");
	PrintArray2D(b);
	printf("c:\n");
	PrintArray2D(c);
	

	FreeArray2D(a);
	FreeArray2D(b);
	FreeArray2D(c);

	return(0);
}

#endif

	

	



