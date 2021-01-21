#include <stdio.h>      /* printf */
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */
#include <string.h>

int main (int argc, char* argv[])
{
  int i;
  printf ("Checking if processor is available...");
  if (system(NULL)) puts ("Ok");
    else exit (EXIT_FAILURE);
  char comm[100];
  char* opt1 = argv[1];
  char* freq = argv[2];
  strcat(comm, "sudo cpupower frequency-set ");
  strcat(comm, opt1);
  strcat(comm, " ");
  strcat(comm, freq);

  printf ("Scaling CPU...\n");
  i = system (comm);
  printf ("The value returned was: %d.\n",i);
  return 0;
}
