#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define N 128

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

void multiply(double mat1[][N], double mat2[][N], double res[][N]) {
    int i, j, k;
    struct timespec req, rem;
    req.tv_sec = 0;
    req.tv_nsec = 0;
    // int ret = nsleep(10);
    for (i = 0; i < N; i++) {
	    // int ret = nsleep(0.00001);
	    nanosleep(&req, &rem);
        for (j = 0; j < N; j++) {
            res[i][j] = 0;
	    // int ret = nsleep(1);
            for (k = 0; k < N; k++) {
                res[i][j] += mat1[i][k] * mat2[k][j];
            }
        }
    }
}

double genRandom() {
    return (double) rand() / RAND_MAX * 2.0 - 1.0;
}

int main() {
    // Initialize matrix by doubles
    srand(time(NULL));

    double res[N][N];
    double mat1[N][N];
    double mat2[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            mat1[i][j] = genRandom();
            mat2[i][j] = genRandom();
        }
    }
    
    clock_t c0 = clock();
    for (int i = 0; ; i++) {
	    multiply(mat1, mat2, res);
    }
    clock_t c1 = clock();
    double runtime_diff_ms = (c1 - c0) * 1000. / CLOCKS_PER_SEC;
    
    printf ("Time : %f \n", runtime_diff_ms);
    // for (int i = 0; i < N; i++) {
    //     for (int j = 0; j < N; j++) {
    //         printf("res : %f\n", res[i][j]);
    //     }
    // }
    return 0;
}
