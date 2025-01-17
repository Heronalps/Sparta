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

