#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <time.h>

#include "array.h"



#define EL(a,i,j,r) ((a)[(i)*(r)+(j)])

int nsleep(long milliseconds) {
    struct timespec req, rem;

    if (milliseconds > 999) {
        req.tv_sec = (int) (milliseconds / 1000);
        req.tv_nsec = (milliseconds - ((long) req.tv_sec * 1000)) * 1000000;
    }
    else {
        req.tv_sec = 0;
        req.tv_nsec = milliseconds * 1000000;
    }

    return nanosleep(&req, &rem);
}

int MultiplyArray2D(Array2D *a, Array2D *b, Array2D *c)
{
	int i;
	int j;
	int k;
	double acc;
	int new_r;
	int new_c;
	double *data;

	if(a->xdim != b->ydim)
	{
		return(-1);
	}

	new_r = a->ydim;
	new_c = b->xdim;

	if(c->ydim != new_r) {
		return(-1);
	}

	if(c->xdim != new_c) {
		return(-1);
	}

	data = c->data;
	for(i=0; i < new_r; i++)
	{
		nsleep(10);		
		for(j=0; j < new_c; j++)
		{
			acc = 0.0;
			// nsleep(10);
			for(k=0; k < a->xdim; k++)
			{
				// nsleep(10);
				acc += (a->data[i*(a->xdim)+k] *
					b->data[k*(b->xdim)+j]);
			}
			data[i*new_c+j] = acc;
		}
	}

	return(1);
}

#ifdef STANDALONE

int main(int argc, char *argv[])
{
	int i;
	int j;
	Array2D *a;
	Array2D *b;
	Array2D *c;
	int err;

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

	err = MultiplyArray2D(a,b,c);

	if(err < 0)
	{
		printf("failed\n");
	}
	else
	{
		printf("a:\n");
		PrintArray2D(a);
		printf("b:\n");
		PrintArray2D(b);
		printf("c:\n");
		PrintArray2D(c);
	}

	FreeArray2D(a);
	FreeArray2D(b);
	FreeArray2D(c);

	return(0);
}

#endif

	

	



