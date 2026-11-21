#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_N 2048

static double A[MAX_N][MAX_N];
static double B[MAX_N][MAX_N];
static double C[MAX_N][MAX_N];

double get_time()
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(int argc, char *argv[])
{
    int N = 512;

    if (argc > 1)
        N = atoi(argv[1]);

    if (N < 1 || N > MAX_N)
    {
        printf("Matrix size must be between 1 and %d\n", MAX_N);
        return 1;
    }

    // Initialize matrices
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            A[i][j] = 1.0;
            B[i][j] = 2.0;
            C[i][j] = 0.0;
        }
    }

    // Start timer
    double start = get_time();

    // Sequential matrix multiplication
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            for (int k = 0; k < N; k++)
            {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    double end = get_time();

    // Verify result
    int correct = 1;

    for (int i = 0; i < N && correct; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (C[i][j] != 2.0 * N)
            {
                correct = 0;
                break;
            }
        }
    }

    printf("SEQUENTIAL MATRIX MULTIPLICATION\n");
    printf("Matrix Size: %d x %d\n", N, N);
    printf("Execution Time: %.6f seconds\n", end - start);
    printf("Result C[0][0]: %.2f\n", C[0][0]);
    printf("Verification: %s\n", correct ? "PASSED" : "FAILED");

    return correct ? 0 : 1;
}
