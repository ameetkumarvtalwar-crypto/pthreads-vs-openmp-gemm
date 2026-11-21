
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <math.h>
#include <time.h>
#include <cblas.h>

typedef struct
{
    int row_start, row_end;
    int col_start, col_end;
    int N;
    float *A, *B, *C;
} ThreadData;

double get_time()
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

void *multiply(void *arg)
{
    ThreadData *d = (ThreadData *)arg;
    int N = d->N;

    for (int i = d->row_start; i < d->row_end; i++)
    {
        for (int j = d->col_start; j < d->col_end; j++)
        {
            float sum = 0.0f;

            for (int k = 0; k < N; k++)
            {
                sum += d->A[i * N + k] * d->B[k * N + j];
            }

            d->C[i * N + j] = sum;
        }
    }

    return NULL;
}

int main(int argc, char *argv[])
{
    int N = 512;
    int num_threads = 4;

    if (argc > 1) N = atoi(argv[1]);
    if (argc > 2) num_threads = atoi(argv[2]);

    if (N < 1 || N > 2048 ||
        num_threads < 1 || num_threads > 12)
    {
        printf("Invalid matrix size or thread count\n");
        return 1;
    }

    int blocks = (int)sqrt(num_threads);

    while (num_threads % blocks != 0)
        blocks--;

    int row_blocks = blocks;
    int col_blocks = num_threads / blocks;

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

    pthread_t threads[12];
    ThreadData data[12];

    int t = 0;

    double start = get_time();

    for (int r = 0; r < row_blocks; r++)
    {
        for (int c = 0; c < col_blocks; c++)
        {
            data[t].row_start = r * N / row_blocks;
            data[t].row_end = (r + 1) * N / row_blocks;

            data[t].col_start = c * N / col_blocks;
            data[t].col_end = (c + 1) * N / col_blocks;

            data[t].N = N;
            data[t].A = A;
            data[t].B = B;
            data[t].C = C;

            if (pthread_create(&threads[t], NULL,
                               multiply, &data[t]) != 0)
            {
                printf("Thread creation failed\n");
                return 1;
            }

            t++;
        }
    }

    for (int i = 0; i < num_threads; i++)
        pthread_join(threads[i], NULL);

    double end = get_time();

    cblas_sgemm(
        CblasRowMajor, CblasNoTrans, CblasNoTrans,
        N, N, N, 1.0f,
        A, N, B, N, 0.0f, reference, N
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

    printf("\nPTHREADS 2D BLOCK MATRIX MULTIPLICATION\n");
    printf("Matrix Size: %d x %d\n", N, N);
    printf("Number of Threads: %d\n", num_threads);
    printf("Row Blocks: %d\n", row_blocks);
    printf("Column Blocks: %d\n", col_blocks);
    printf("Execution Time: %.6f seconds\n", end - start);
    printf("Relative Error: %.8e\n", relative_error);
    printf("Verification: %s\n", correct ? "PASSED" : "FAILED");

    free(A);
    free(B);
    free(C);
    free(reference);

    return correct ? 0 : 1;
}

