// Cost of OS threads on this machine: create+join, and a context switch
// measured with two threads ping-ponging one byte through a pair of pipes.
#include <pthread.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}
static void *noop(void *arg) { return arg; }

static int a2b[2], b2a[2];
static const int ROUNDS = 200000;
static void *pong(void *arg) {
    char c;
    for (int i = 0; i < ROUNDS; i++) {
        if (read(a2b[0], &c, 1) != 1) break;
        if (write(b2a[1], &c, 1) != 1) break;
    }
    return arg;
}

int main(void) {
    const int N = 20000;
    double t0 = now();
    for (int i = 0; i < N; i++) {
        pthread_t t;
        pthread_create(&t, NULL, noop, NULL);
        pthread_join(t, NULL);
    }
    printf("thread create+join: %.1f us\n", (now() - t0) / N * 1e6);

    pthread_attr_t attr;
    size_t stack;
    pthread_attr_init(&attr);
    pthread_attr_getstacksize(&attr, &stack);
    printf("default thread stack (virtual): %zu KB\n", stack / 1024);

    if (pipe(a2b) != 0 || pipe(b2a) != 0) return 1;
    pthread_t t;
    pthread_create(&t, NULL, pong, NULL);
    char c = 'x';
    t0 = now();
    for (int i = 0; i < ROUNDS; i++) {
        if (write(a2b[1], &c, 1) != 1 || read(b2a[0], &c, 1) != 1) return 1;
    }
    double dt = now() - t0;
    pthread_join(t, NULL);
    printf("thread switch (pipe ping-pong): %.2f us per switch\n", dt / (2.0 * ROUNDS) * 1e6);
    return 0;
}
