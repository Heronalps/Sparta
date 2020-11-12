// gcc -fopenmp -o go multicore.c
// ./go

#include <stdio.h>
#include <omp.h>

int main(int argc, char **argv)
{
  int i, thread_id, nloops;

#pragma omp parallel private(thread_id, nloops)
  {
    nloops = 0;

#pragma omp for
    for (i=0; i < 1000; ++i)
      {
        while(1);
      }

    thread_id = omp_get_thread_num();

    printf("Thread %d performed %d iterations of the loop.\n",
           thread_id, nloops );
  }

  return 0;
}
