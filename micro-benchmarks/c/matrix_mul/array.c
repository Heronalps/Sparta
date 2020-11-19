#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "array.h"

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

	
	

