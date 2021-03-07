#include <stdio.h>
#include <stdlib.h>

int readmatrix(size_t n, float (*a)[n], const char* filename)
{
    FILE *pf;
    pf = fopen (filename, "r");
    if (pf == NULL)
        return 0;

    for(size_t i = 0; i < n; ++i)
    {
        for(size_t j = 0; j < n; ++j)
            fscanf(pf, "%f", a[i] + j);
    }

    fclose (pf); 
    return 1; 
}

void savematrix(size_t n, float (*matrix)[n], const char* filename) { 
    int i, j;
    FILE *f1;
    f1 = fopen(filename, "w");
    if (f1 == NULL) {
        printf("file could not be opened");
        return;
    }
     
    for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
            fprintf(f1,"%5.2f ", matrix[i][j]);
        }
        fprintf(f1,"\n");
    }
    fclose(f1);
}

int main(void)
{
    size_t n = 3;
    float matrix[n][n];

    readmatrix(n, matrix, "mat.txt");

    for(size_t i = 0; i < n; ++i)
    {
        for(size_t j = 0; j < n; ++j)
            printf("%5.2f ", matrix[i][j]);
        puts("");
    }

    savematrix(n, matrix, "mat2.txt");

    return 0;
}