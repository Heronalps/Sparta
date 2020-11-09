#include <stdio.h>
#define N 128

void multiply(int mat1[N][N], int mat2[N][N], int res[N][N]) {
    int i, j, k;
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            res[i][j] = 0;
            for (k = 0; k < N; k++) {
                res[i][j] += mat1[i][k] * mat2[k][j];
            }
        }
    }
}

int main() {
    // Initialize matrix by doubles
    int res[N][N];
    multiply(mat1, mat2, res);
    return 0;
}
