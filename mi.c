#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>

#define handle_error(msg) \
	do { perror(msg); exit(EXIT_FAILURE); } while (0)

#define NUM_BYTES 256
#define BUFSIZE 256

struct filectx {
	int fd;
	size_t idx;
	off_t size;
	uint8_t *file;
	float prob[NUM_BYTES];
	float entropy;
} ;

static inline void load_file(struct filectx *ctx, char *filename, size_t idx) {
	struct stat statb;

	ctx->idx = idx;

	ctx->fd = open(filename, O_RDONLY);
	if(ctx->fd == -1)
		handle_error("open");

        if (fstat(ctx->fd, &statb) == -1)           /* To obtain file size */
               handle_error("fstat");

	if(statb.st_size == 0) {
		fprintf(stderr, "One of the data files is empty\n");
		exit(EXIT_FAILURE);
	}

	ctx->size = statb.st_size;

	ctx->file = mmap(NULL, statb.st_size, PROT_READ, MAP_PRIVATE, ctx->fd, 0);
	if(ctx->file == MAP_FAILED)
		handle_error("mmap");
}

static inline void compute_freqs(struct filectx *f) {
	for(size_t i = 0; i < NUM_BYTES; i++)
		f->prob[i] = 0.;

	for(off_t i = 0; i < f->size; i++)
		f->prob[f->file[i]] += 1.;

	f->entropy = 0.;
	for(size_t i=0; i < NUM_BYTES; i++) {
		f->prob[i] /= f->size;
		if(f->prob[i] > 0.)
			f->entropy -= f->prob[i]*log2f(f->prob[i]);
	}
}

static inline void update_progress(int progress, int total, unsigned int width) {
	for(unsigned int i=0; i<(2*width+3); i++)
		fputc('\b', stderr);
	fprintf(stderr, "%*d / %*d", width, progress, width, total);
}

static inline float compute_vi(struct filectx *fa, struct filectx *fb) {
	size_t size_shared = (fa->size <= fb->size) ? fa->size : fb->size;

	unsigned long int joint_freq[NUM_BYTES*NUM_BYTES];

	// zero joint frequencies
	for(size_t i = 0; i < NUM_BYTES; i++)
		for(size_t j = 0; j < NUM_BYTES; j++)
			joint_freq[i*NUM_BYTES+j] = 0;

	// count joint frequencies
	for(size_t i = 0; i < size_shared; i++) {
		size_t idx = fa->file[i]*NUM_BYTES + fb->file[i];
		joint_freq[idx]++;
	}

	// compute mutual information and joint entropy
	float mi = 0.;
//	float  h = 0.;
	for(size_t i = 0; i < NUM_BYTES; i++) {
		for(size_t j = 0; j < NUM_BYTES; j++) {
			if(joint_freq[i*NUM_BYTES + j] > 0) {
				float jp = ((float)joint_freq[i*NUM_BYTES + j]) / size_shared;

				mi += jp * log2f(jp / (fa->prob[i] * fb->prob[j]));
//				h  -= jp * log2f(jp);
			}
		}
	}

	// compute and return variation of information
/*
	float vi;
	if(mi == 0. && h == 0.) {
		vi = 0.;
	} else if(mi > h) {
		vi = 0.;
	} else {
		vi = 1. - (mi/h);
	}
*/

	return mi;
}

#define NUMFMT "%10.8f"

int main(int argc, char **argv) {
	struct filectx *files;

	// parse args
	if(argc < 3) {
		fprintf(stderr, "Usage: %s <output-file> <input-files...>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// load files
	int n_files = argc-2;

	files = malloc(n_files * sizeof(struct filectx));

	fprintf(stderr, "Loading %d files... 0000 / 0000", n_files);
	for(int i = 0; i < n_files; i++)
		load_file(&files[i], argv[2+i], i);

	// estimate byte frequencies for files separately
	fprintf(stderr, "\nComputing per-file byte frequencies...\n");
	fprintf(stderr, "\t0000 / 0000");
#pragma omp parallel for schedule(dynamic)
	for(int f = 0; f < n_files; f++) {
#pragma omp critical
		{
			update_progress(f, n_files, 4);
		}
		compute_freqs(&files[f]);
	}

	// compute variation of information for each pair
	fprintf(stderr, "\nComputing pairwise VI... 00000000 / 00000000");
	size_t total = n_files * (n_files+1) / 2;
	float *vi = malloc(sizeof(float) * total);

#pragma omp parallel for schedule(dynamic)
	for(int fa = 0; fa < n_files; fa++) {
		int ia = fa*(fa+1)/2;

#pragma omp critical
		{
			update_progress(ia, total, 8);
		}

		for(int fb = 0; fb < fa; fb++)
			vi[ia+fb] = compute_vi(&files[fa], &files[fb]);
	}

	// output entropies
	fprintf(stderr, "\nWriting entropies... 0000 / 0000");

	char namebuf[BUFSIZE];
	strncpy(namebuf, argv[1],  BUFSIZE);
	strncat(namebuf, ".ent", BUFSIZE);
	FILE *outf = fopen(namebuf, "w");
	for(int f = 0; f < n_files; f++) {
		fprintf(outf, NUMFMT "\n", files[f].entropy);
		update_progress(f, n_files, 4);
	}

	// output VIs
	fprintf(stderr, "\nWriting VI data... 00000000 / 00000000");
	strncpy(namebuf, argv[1],   BUFSIZE);
	strncat(namebuf, ".vi", BUFSIZE);
	outf = fopen(namebuf, "w");

	for(int fa = 0; fa < n_files; fa++) {
		update_progress(fa*n_files, n_files*n_files, 8);

		int ia = fa*(fa+1)/2;

		for(int fb = 0; fb < fa; fb++) {
			if(fb>0) fputc(',', outf);
			fprintf(outf, NUMFMT, vi[ia+fb]);
		}

		for(int fb = fa; fb < n_files; fb++) {
			if(fb>0) fputc(',', outf);
			fprintf(outf, NUMFMT, 0.);
		}

		fprintf(outf, "\n");
	}

	fprintf(stderr, "\nDone.\n");

	for(int i=0; i < n_files; i++)
		close(files[i].fd);

	free(files);
}
