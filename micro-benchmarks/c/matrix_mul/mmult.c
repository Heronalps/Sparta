#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <pthread.h>

#include "c-timer.h"

#ifndef ARRAY_H
#define ARRAY_H

struct array_stc_2d
{
        int xdim;
        int ydim;
        double *data;
};

typedef struct array_stc_2d Array2D;
Array2D *MakeArray2D(int ydim, int xdim);
void FreeArray2D(Array2D *a);
void PrintArray2D(Array2D *a);
Array2D *CopyArray2D(Array2D *a);
Array2D *TransposeArray2D(Array2D *a);

/*
 * choose 1D to be column vectors
 */

#define Array1D Array2D
#define MakeArray1D(dim) MakeArray2D(1,(dim))
#define FreeArray1D(a) FreeArray2D(a)
#define PrintArray1D(a) PrintArray2D(a)
#define CopyArray1D(a) CopyArray2D(a)
#define TransposeArray1D(a) TransposeArray2D(a)

#endif

Array2D *MakeArray2D(int ydim, int xdim)
{
	Array2D *a;

	a = (Array2D *)malloc(sizeof(Array2D));
	if(a == NULL)
	{
		return(NULL);
	}

	a->data = (double *)malloc(xdim*ydim*sizeof(double));
	if(a->data == NULL)
	{
		free(a);
		return(NULL);
	}

	a->xdim = xdim;
	a->ydim = ydim;
	memset(a->data,0,xdim*ydim*sizeof(double));

	return(a);
}

void FreeArray2D(Array2D *a)
{
	free(a->data);
	free(a);
	return;
}

void PrintArray2D(Array2D *a)
{
	int i;
	int j;

	for(i=0; i < a->ydim; i++)
	{
		fprintf(stdout,"\t[");
		for(j=0; j < a->xdim; j++)
		{
			if(j < a->xdim-1)
			{
				fprintf(stdout,"%f ",a->data[i*a->xdim+j]);
			}
			else
			{
				fprintf(stdout,"%f]\n",a->data[i*a->xdim+j]);
			}
		}
	}

	return;
}

Array2D *CopyArray2D(Array2D *a)
{
	Array2D *b;
	int i;

	b = MakeArray2D(a->ydim,a->xdim);
	if(b == NULL)
	{
		return(NULL);
	}

	for(i=0; i < ((a->xdim)*(a->ydim)); i++)
	{
		b->data[i] = a->data[i];
	}

	return(b);
}

Array2D *TransposeArray2D(Array2D *a)
{
	Array2D *t;
	int i;
	int j;

	t = MakeArray2D(a->xdim,a->ydim);
	if(t == NULL)
	{
		return(NULL);
	}

	for(i=0; i < a->ydim; i++)
	{
		for(j=0; j < a->xdim; j++)
		{
			t->data[j*t->xdim+i] =
				a->data[i*a->xdim+j];
		}
	}

	return(t);
}

	
#ifndef READ_MATRIX_H
#define READ_MATRIX_H

Array2D *ReadMatrix(char *fname);
void PrintMatrix(Array2D *m);

#endif

	
int IsComment(char *buf, int size) {
	int i;

	if(buf[0] == '\n') {
		return(1);
	}
	for(i=0; i < size; i++) {
		if(buf[i] == '#') {
			return(1);
		}
		if(buf[i] == 0) {
			break;
		}
	}

	return(0);
}

Array2D *ReadMatrix(char *fname)
{
	int rows;
	int cols;
	char line_buf[4096];
	Array2D *array;
	int err;
	FILE *fd;
	char *s;
	char *next;
	int i;
	int j;

	fd = fopen(fname,"r");
	if(fd == NULL) {
		fprintf(stderr,"couldn't open %s\n",fname);
		return(NULL);
	}

	memset(line_buf,0,sizeof(line_buf));
	s = fgets(line_buf,sizeof(line_buf)-1,fd);
	if(s == NULL) {
		fprintf(stderr,"couldn't read dimensions from %s\n",
			fname);
		fclose(fd);
		return(NULL);
	}
	while(IsComment(line_buf,sizeof(line_buf))) {
		memset(line_buf,0,sizeof(line_buf));
		s = fgets(line_buf,sizeof(line_buf)-1,fd);
		if(s == NULL) {
			fprintf(stderr,"couldn't read dimensions from %s\n",
				fname);
			fclose(fd);
			return(NULL);
		}
	}

	rows = strtol(line_buf,&next,10);
	cols = strtol(next,NULL,10);

	if(rows <= 0) {
		fprintf(stderr,"invalid rows %d in %s\n",
				rows,line_buf);
		fclose(fd);
		return(NULL);
	}

	if(cols <= 0) {
		fprintf(stderr,"invalid cols %d in %s\n",
				cols,line_buf);
		fclose(fd);
		return(NULL);
	}

	array = MakeArray2D(rows,cols);
	if(array == NULL) {
		fclose(fd);
		return(NULL);
	}

	i = 0;
	while(i < rows) {
		j = 0;
		while(j < cols) {
			memset(line_buf,0,sizeof(line_buf));
			s = fgets(line_buf,sizeof(line_buf)-1,fd);
			if(s == NULL) {
				break;
			}
			while(IsComment(line_buf,sizeof(line_buf))) {
				memset(line_buf,0,sizeof(line_buf));
				s = fgets(line_buf,sizeof(line_buf)-1,fd);
				if(s == NULL) {
					break;
				}
			}
			if(s == NULL) {
				break;
			}
			array->data[i*cols+j] = strtod(line_buf,NULL);
			j++;
		}
		if(s == NULL) {
			break;
		}
		i++;
	}

	if(i != rows) {
		fprintf(stderr,"error: read %d of %d rows from %s\n",
				i+1,
				rows,
				fname);
		FreeArray2D(array);
		fclose(fd);
		return(NULL);
	}
	if(j != cols) {
		fprintf(stderr,"error: read %d of %d cols at row %d from %s\n",
				j+1,
				cols,
				i+1,
				fname);
		FreeArray2D(array);
		fclose(fd);
		return(NULL);
	}

	fclose(fd);
	return(array);
}

void PrintMatrix(Array2D *m)
{
	int i;
	int j;

	printf("%d %d\n",m->ydim,m->xdim);
	for(i=0; i < m->ydim; i++) {
		printf("# Row %d\n",i);
		for(j=0; j < m->xdim; j++) {
			printf("%f\n",m->data[i*m->xdim+j]);
		}
	}

	return;
}
	

#ifdef STANDALONE

char *Usage = "read-matrix -f filename\n";
#define ARGS "f:"

char Fname[4096];

int main(int argc, char **argv)
{
	int c;
	Array2D *array;

	while((c = getopt(argc,argv,ARGS)) != EOF) {
		switch(c) {
			case 'f':
				strncpy(Fname,optarg,sizeof(Fname));
				break;
			default:
				fprintf(stderr,"unrecognized command %c\n",
					(char)c);
				fprintf(stderr,"usage: %s",Usage);
				exit(1);
		}
	}

	if(Fname[0] == 0) {
		fprintf(stderr,"must specify file name\n");
		fprintf(stderr,"usage: %s",Usage);
		exit(1);
	}
	array = ReadMatrix(Fname);

	if(array == NULL) {
		fprintf(stderr,"array read failed\n");
		exit(1);
	}

	printf("successfully read matrix with %d rows and %d cols from %s\n",
			array->ydim,
			array->xdim,
			Fname);
	FreeArray2D(array);

	exit(0);
}

#endif

#ifndef MATRIX_MULTIPLY_THREAD_H
#define MATRIX_MULTIPLY_THREAD_H

struct mm_struct
{
        int id;
        Array2D *a;
        Array2D *b;
        Array2D *c;
        int starting_row;
        int row_range;
        int starting_col;
        int col_range;
};

typedef struct mm_struct MM_arg;

void *MMThread(void *arg);

#endif



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

	

	



