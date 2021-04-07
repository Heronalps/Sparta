#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include <sys/time.h>
#include <string.h>

#include "array.h"

int IsComment(char *buf, int size) {
	int i;

	if(buf[0] == '\n') {
		return(1);
	}
	for(i=0; i < size; i++) {
		if(buf[i] == '#') {
			return(1);
		}
		if(buf[i] == 0) {
			break;
		}
	}

	return(0);
}

Array2D *ReadMatrix(char *fname)
{
	int rows;
	int cols;
	char line_buf[4096];
	Array2D *array;
	int err;
	FILE *fd;
	char *s;
	char *next;
	int i;
	int j;

	fd = fopen(fname,"r");
	if(fd == NULL) {
		fprintf(stderr,"couldn't open %s\n",fname);
		return(NULL);
	}

	memset(line_buf,0,sizeof(line_buf));
	s = fgets(line_buf,sizeof(line_buf)-1,fd);
	if(s == NULL) {
		fprintf(stderr,"couldn't read dimensions from %s\n",
			fname);
		fclose(fd);
		return(NULL);
	}
	while(IsComment(line_buf,sizeof(line_buf))) {
		memset(line_buf,0,sizeof(line_buf));
		s = fgets(line_buf,sizeof(line_buf)-1,fd);
		if(s == NULL) {
			fprintf(stderr,"couldn't read dimensions from %s\n",
				fname);
			fclose(fd);
			return(NULL);
		}
	}

	rows = strtol(line_buf,&next,10);
	cols = strtol(next,NULL,10);

	if(rows <= 0) {
		fprintf(stderr,"invalid rows %d in %s\n",
				rows,line_buf);
		fclose(fd);
		return(NULL);
	}

	if(cols <= 0) {
		fprintf(stderr,"invalid cols %d in %s\n",
				cols,line_buf);
		fclose(fd);
		return(NULL);
	}

	array = MakeArray2D(rows,cols);
	if(array == NULL) {
		fclose(fd);
		return(NULL);
	}

	i = 0;
	while(i < rows) {
		j = 0;
		while(j < cols) {
			memset(line_buf,0,sizeof(line_buf));
			s = fgets(line_buf,sizeof(line_buf)-1,fd);
			if(s == NULL) {
				break;
			}
			while(IsComment(line_buf,sizeof(line_buf))) {
				memset(line_buf,0,sizeof(line_buf));
				s = fgets(line_buf,sizeof(line_buf)-1,fd);
				if(s == NULL) {
					break;
				}
			}
			if(s == NULL) {
				break;
			}
			array->data[i*cols+j] = strtod(line_buf,NULL);
			j++;
		}
		if(s == NULL) {
			break;
		}
		i++;
	}

	if(i != rows) {
		fprintf(stderr,"error: read %d of %d rows from %s\n",
				i+1,
				rows,
				fname);
		FreeArray2D(array);
		fclose(fd);
		return(NULL);
	}
	if(j != cols) {
		fprintf(stderr,"error: read %d of %d cols at row %d from %s\n",
				j+1,
				cols,
				i+1,
				fname);
		FreeArray2D(array);
		fclose(fd);
		return(NULL);
	}

	fclose(fd);
	return(array);
}

void PrintMatrix(Array2D *m)
{
	int i;
	int j;

	printf("%d %d\n",m->ydim,m->xdim);
	for(i=0; i < m->ydim; i++) {
		printf("# Row %d\n",i);
		for(j=0; j < m->xdim; j++) {
			printf("%f\n",m->data[i*m->xdim+j]);
		}
	}

	return;
}
	

#ifdef STANDALONE

char *Usage = "read-matrix -f filename\n";
#define ARGS "f:"

char Fname[4096];

int main(int argc, char **argv)
{
	int c;
	Array2D *array;

	while((c = getopt(argc,argv,ARGS)) != EOF) {
		switch(c) {
			case 'f':
				strncpy(Fname,optarg,sizeof(Fname));
				break;
			default:
				fprintf(stderr,"unrecognized command %c\n",
					(char)c);
				fprintf(stderr,"usage: %s",Usage);
				exit(1);
		}
	}

	if(Fname[0] == 0) {
		fprintf(stderr,"must specify file name\n");
		fprintf(stderr,"usage: %s",Usage);
		exit(1);
	}
	array = ReadMatrix(Fname);

	if(array == NULL) {
		fprintf(stderr,"array read failed\n");
		exit(1);
	}

	printf("successfully read matrix with %d rows and %d cols from %s\n",
			array->ydim,
			array->xdim,
			Fname);
	FreeArray2D(array);

	exit(0);
}

#endif
