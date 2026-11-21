#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define MAX_THREADS 12

// Packed counters: multiple counters may share a cache line
volatile long long packed[MAX_THREADS];

// Padded counters: each counter is aligned to a separate cache line
struct PaddedCounter {
    _Alignas(64) volatile long long value;
};

struct PaddedCounter padded[MAX_THREADS];

typedef struct {
    int id;
    long long iterations;
    volatile long long *counter;
} ThreadData;

double get_time() {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

void *update_counter(void *arg) {
    ThreadData *data = (ThreadData *)arg;

    for (long long i = 0; i < data->iterations; i++) {
        (*data->counter)++;
    }

    return NULL;
}

double run_test(int num_threads, long long iterations, int use_padding) {
    pthread_t threads[MAX_THREADS];
    ThreadData data[MAX_THREADS];

    double start = get_time();

    for (int i = 0; i < num_threads; i++) {
        data[i].id = i;
        data[i].iterations = iterations;

        if (use_padding)
            data[i].counter = &padded[i].value;
        else
            data[i].counter = &packed[i];

        pthread_create(&threads[i], NULL, update_counter, &data[i]);
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    return get_time() - start;
}

int main(int argc, char *argv[]) {
    int num_threads = 4;
    long long iterations = 50000000;

    if (argc > 1)
        num_threads = atoi(argv[1]);

    if (num_threads < 1 || num_threads > MAX_THREADS) {
        printf("Use between 1 and %d threads.\n", MAX_THREADS);
        return 1;
    }

    printf("FALSE SHARING EXPERIMENT\n");
    printf("Number of Threads: %d\n", num_threads);
    printf("Iterations per Thread: %lld\n", iterations);

    double packed_time = run_test(num_threads, iterations, 0);
    double padded_time = run_test(num_threads, iterations, 1);

    printf("\nPacked Array Time: %.6f seconds\n", packed_time);
    printf("Padded Array Time: %.6f seconds\n", padded_time);

    if (packed_time > padded_time)
        printf("Padding improved performance.\n");
    else
        printf("Padding did not improve performance in this run.\n");

    return 0;
}
