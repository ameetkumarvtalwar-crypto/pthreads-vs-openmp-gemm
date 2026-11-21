#define _POSIX_C_SOURCE 199309L

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <math.h>
#include <cblas.h>

#define RANDOM_SEED 42

typedef struct {
    int start_row;
    int end_row;
    int N;
    float *A;
    float *B;
    float *C;
} ThreadData;

double get_time()
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

void* multiply(void* arg)
{
    ThreadData* data = (ThreadData*)arg;

    int N = data->N;
    float *A = data->A;
    float *B = data->B;
    float *C = data->C;

    for (int i = data->start_row; i < data->end_row; i++)
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

    return NULL;
}

int main(int argc, char* argv[])
{
    int N = 512;
    int num_threads = 4;

    if (argc > 1)
        N = atoi(argv[1]);

    if (argc > 2)
        num_threads = atoi(argv[2]);

    if (N < 1 || num_threads < 1 || num_threads > 12)
    {
        printf("Usage: ./pthreads <matrix_size> <threads>\n");
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

    pthread_t threads[num_threads];
    ThreadData data[num_threads];

    // Generate the same random matrices as Team 1
    srand(RANDOM_SEED);

    for (size_t i = 0; i < elements; i++)
    {
        A[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
        B[i] = 2.0f * ((float)rand() / RAND_MAX) - 1.0f;
    }

    double total_start = get_time();
    double create_start = get_time();

    for (int t = 0; t < num_threads; t++)
    {
        data[t].start_row = t * N / num_threads;
        data[t].end_row = (t + 1) * N / num_threads;
        data[t].N = N;
        data[t].A = A;
        data[t].B = B;
        data[t].C = C;

        if (pthread_create(&threads[t], NULL, multiply, &data[t]) != 0)
        {
            printf("Thread creation failed\n");

            for (int j = 0; j < t; j++)
                pthread_join(threads[j], NULL);

            free(A);
            free(B);
            free(C);
            free(reference);
            return 1;
        }
    }

    double create_end = get_time();
    double join_start = get_time();

    for (int t = 0; t < num_threads; t++)
        pthread_join(threads[t], NULL);

    double join_end = get_time();
    double total_end = get_time();

    // Verify against OpenBLAS
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

    printf("\nPTHREADS MATRIX MULTIPLICATION\n");
    printf("Matrix Size: %d x %d\n", N, N);
    printf("Number of Threads: %d\n", num_threads);

    printf("Execution Time: %.6f seconds\n",
           total_end - total_start);

    printf("Thread Creation Time: %.6f seconds\n",
           create_end - create_start);

    printf("Thread Joining/Waiting Time: %.6f seconds\n",
           join_end - join_start);

    printf("Relative max-norm error: %.8e\n", relative_error);

    printf("Verification: %s\n",
           relative_error < 1e-4 ? "PASSED" : "FAILED");

    free(A);
    free(B);
    free(C);
    free(reference);

    return relative_error < 1e-4 ? 0 : 1;
}

