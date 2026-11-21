#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <math.h>
#include <cblas.h>

#define RANDOM_SEED 42

int main(int argc, char *argv[])
{
    int N = 512;
    int num_threads = 4;

    if (argc > 1)
        N = atoi(argv[1]);

    if (argc > 2)
        num_threads = atoi(argv[2]);

    if (N < 1 || num_threads < 1 || num_threads > 12)
    {
        printf("Usage: ./openmp <matrix_size> <threads>\n");
        return 1;
    }

    size_t elements = (size_t)N * N;

    float *A = malloc(elements * sizeof(float));
    float *B = malloc(elements * sizeof(float));
    float *C = calloc(elements, sizeof(float));
    float *reference = calloc(elements, sizeof(float));

    if (!A || !B || !C || !reference)
    {
        printf("Memory allocation failed\n");
        free(A);
        free(B);
        free(C);
        free(reference);
        return 1;
    }

    // Generate same random matrices as Team 1
    srand(RANDOM_SEED);

    for (size_t i = 0; i < elements; i++)
    {
        A[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
        B[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
    }

    omp_set_dynamic(0);
    omp_set_num_threads(num_threads);

    double start = omp_get_wtime();

    // Parallel matrix multiplication
    #pragma omp parallel for schedule(runtime)
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            float sum = 0.0f;

            for (int k = 0; k < N; k++)
            {
                sum += A[i * N + k] * B[k * N + j];
            }

            C[i * N + j] = sum;
        }
    }

    double end = omp_get_wtime();

    // Verify using OpenBLAS
    cblas_sgemm(
        CblasRowMajor,
        CblasNoTrans,
        CblasNoTrans,
        N, N, N,
        1.0f,
        A, N,
        B, N,
        0.0f,
        reference, N
    );

    float max_error = 0.0f;
    float max_reference = 0.0f;

    for (size_t i = 0; i < elements; i++)
    {
        float error = fabsf(C[i] - reference[i]);

        if (error > max_error)
            max_error = error;

        if (fabsf(reference[i]) > max_reference)
            max_reference = fabsf(reference[i]);
    }

    float relative_error =
        max_reference == 0.0f
        ? max_error
        : max_error / max_reference;

    printf("\nOPENMP MATRIX MULTIPLICATION\n");
    printf("Matrix Size: %d x %d\n", N, N);
    printf("Number of Threads: %d\n", num_threads);
    printf("Execution Time: %.6f seconds\n", end - start);
    printf("Relative max-norm error: %.8e\n", relative_error);

    printf("Verification: %s\n",
           relative_error < 1e-4 ? "PASSED" : "FAILED");

    free(A);
    free(B);
    free(C);
    free(reference);

    return relative_error < 1e-4 ? 0 : 1;
}

