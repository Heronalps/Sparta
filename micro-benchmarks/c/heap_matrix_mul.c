#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>
#define N 6000
#define M 1 

struct matrix_s {
    char matrixName[50];
    size_t columns;
    size_t rows;
    float* data;
};

typedef struct matrix_s matrix_t;

void m_init(matrix_t *t, size_t columns, size_t rows) {
    t->rows = rows;
    t->columns = columns;
    t->data = calloc(rows * columns, sizeof(*t->data));
    if (t->data == NULL) abort();
}

size_t m_columns(const matrix_t *t) {
    return t->columns;
}

size_t m_rows(const matrix_t *t) {
    return t->rows;
}

// matrix_get 
// (x,y) = (col,row) always in that order
float *m_get(const matrix_t *t, size_t x, size_t y) {
    // assert(x < m_columns(t));
    // assert(y < m_rows(t));
    // __UNCONST
    // see for example `char *strstr(const char *haystack, ...` 
    // it takes `const char*` but returns `char*` nonetheless.
    return (float*)&t->data[t->rows * x + y];
}

// fill matrix with a fancy patterns just so it's semi-unique
void m_init_seq(matrix_t *t, size_t columns, size_t rows) {
    m_init(t, columns, rows);
    for (size_t i = 0; i < t->columns; ++i) {
        for (size_t j = 0; j < t->rows; ++j) {
            *m_get(t, i, j) = i + 100 * j;
        }
    }
}

void m_print(const matrix_t *t) {
    printf("matrix %p\n", (void*)t->data);
    for (size_t i = 0; i < t->columns; ++i) {
        for (size_t j = 0; j < t->rows; ++j) {
            printf("%5g\t", *m_get(t, i, j));
        }
        printf("\n");
    }
    printf("\n");
}

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

void m_multiply(matrix_t *out, const matrix_t *a, const matrix_t *b) {
    // assert(m_columns(b) == m_rows(a));
    // assert(m_columns(out) == m_columns(a));
    // assert(m_rows(out) == m_rows(b));
    // Index from 0, not from 1
    // don't do `(col-1) + (row-1)` strange things
    for (size_t col = 0; col < m_columns(out); ++col) {
        // nsleep(M);
	// printf("col : %d \n", col);
        for (size_t row = 0; row < m_rows(out); ++row) {
           //  nsleep(M);
	   // printf("row : %d \n", row);
            float sum = 0;
            for (size_t i = 0; i < m_rows(a); ++i) {
                // nsleep(M);
		// printf("i : %d \n", i);
                *m_get(out, col, row) += *m_get(a, col, i) * *m_get(b, i, row);
            }
            // *m_get(out, col, row) = sum;
        }
    }
}

int main()
{
    matrix_t our_matrix[100];

    m_init_seq(&our_matrix[0], N, N);
    m_init_seq(&our_matrix[1], N, N);

    // m_print(&our_matrix[0]);
    // m_print(&our_matrix[1]);

    m_init(&our_matrix[2], N, N);
    clock_t c0 = clock();
    m_multiply(&our_matrix[2], &our_matrix[0], &our_matrix[1]);
    clock_t c1 = clock();
    double runtime_diff_ms = (c1 - c0) * 1.0 / CLOCKS_PER_SEC;
    printf ("Time : %f \n", runtime_diff_ms);
    // m_print(&our_matrix[2]);

    return 0;
}
