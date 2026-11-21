
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include <cblas.h>

int main(int argc, char *argv[])
{
    int N = 512;
    int num_threads = 4;

    if (argc > 1) N = atoi(argv[1]);
    if (argc > 2) num_threads = atoi(argv[2]);

    if (N < 1 || N > 2048 || num_threads < 1 || num_threads > 12)
    {
        printf("Invalid matrix size or thread count\n");
        return 1;
    }

    size_t size = (size_t)N * N;

    float *A = malloc(size * sizeof(float));
    float *B = malloc(size * sizeof(float));
    float *C = calloc(size, sizeof(float));
    float *reference = calloc(size, sizeof(float));

    if (!A || !B || !C || !reference)
    {
        printf("Memory allocation failed\n");
        return 1;
    }

    srand(42);

    for (size_t i = 0; i < size; i++)
    {
        A[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
        B[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
    }

    omp_set_dynamic(0);
    omp_set_num_threads(num_threads);

    double start = omp_get_wtime();

    #pragma omp parallel for collapse(2) schedule(static)
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

    for (size_t i = 0; i < size; i++)
    {
        float error = fabsf(C[i] - reference[i]);

        if (error > max_error)
            max_error = error;

        if (fabsf(reference[i]) > max_reference)
            max_reference = fabsf(reference[i]);
    }

    float relative_error = max_error / max_reference;
    int correct = relative_error < 1e-4f;

    printf("\nOPENMP COLLAPSE(2) MATRIX MULTIPLICATION\n");
    printf("Matrix Size: %d x %d\n", N, N);
    printf("Number of Threads: %d\n", num_threads);
    printf("Execution Time: %.6f seconds\n", end - start);
    printf("Relative Error: %.8e\n", relative_error);
    printf("Verification: %s\n", correct ? "PASSED" : "FAILED");

    free(A);
    free(B);
    free(C);
    free(reference);

    return correct ? 0 : 1;
}

