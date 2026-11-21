#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <math.h>

#define N 8000000
#define REPEATS 10

double *A, *B, *C;
volatile double checksum;

double measure(int operation) {
    double start = omp_get_wtime();

    if (operation == 0) {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < N; i++)
            C[i] = A[i];
    }
    else if (operation == 1) {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < N; i++)
            B[i] = 3.0 * C[i];
    }
    else if (operation == 2) {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < N; i++)
            C[i] = A[i] + B[i];
    }
    else {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < N; i++)
            A[i] = B[i] + 3.0 * C[i];
    }

    double elapsed = omp_get_wtime() - start;

    // Make the computed array values observable.
    double sum = 0.0;

    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < N; i++) {
        if (operation == 0 || operation == 2)
            sum += C[i];
        else if (operation == 1)
            sum += B[i];
        else
            sum += A[i];
    }

    checksum = sum;

    return elapsed;
}

int main(int argc, char *argv[]) {

    int threads = 1;

    if (argc > 1)
        threads = atoi(argv[1]);

    omp_set_dynamic(0);
    omp_set_num_threads(threads);

    A = malloc(N * sizeof(double));
    B = malloc(N * sizeof(double));
    C = malloc(N * sizeof(double));

    if (!A || !B || !C) {
        printf("Memory allocation failed!\n");
        return 1;
    }

    #pragma omp parallel for
    for (int i = 0; i < N; i++) {
        A[i] = 1.0;
        B[i] = 2.0;
        C[i] = 0.0;
    }

    const char *names[] = {
        "Copy", "Scale", "Add", "Triad"
    };

    double bytes[] = {
        2.0 * sizeof(double) * N,
        2.0 * sizeof(double) * N,
        3.0 * sizeof(double) * N,
        3.0 * sizeof(double) * N
    };

    printf("\nOPENMP STREAM BENCHMARK\n");
    printf("Array size: %d elements\n", N);
    printf("Threads: %d\n\n", threads);

    for (int op = 0; op < 4; op++) {

        double total = 0.0;
        double squared = 0.0;

        // Warm-up
        measure(op);

        for (int r = 0; r < REPEATS; r++) {
            double t = measure(op);
            total += t;
            squared += t * t;
        }

        double average = total / REPEATS;

        double variance =
            (squared / REPEATS) - (average * average);

        if (variance < 0.0)
            variance = 0.0;

        double stddev = sqrt(variance);

        double bandwidth = bytes[op] / average / 1e9;

        printf("%s: Average=%.6f s | StdDev=%.6f s | Bandwidth=%.3f GB/s\n",
               names[op], average, stddev, bandwidth);
    }

    printf("\nVerification checksum: %.2f\n", checksum);

    free(A);
    free(B);
    free(C);

    return 0;
}
