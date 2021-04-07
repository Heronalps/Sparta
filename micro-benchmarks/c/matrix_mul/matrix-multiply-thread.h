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

