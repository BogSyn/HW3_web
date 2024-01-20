import multiprocessing
import time


def factorize_worker(num):
    """
            Факторизує список чисел та закидує список в чергу процесів.

            Args:
                *num: Список чисел.

            Returns:
                Список чисел, на які числа з вхідного числа поділяються без залишку.
            """
    factors = [i for i in range(1, num + 1) if num % i == 0]
    return factors


def factorize(*number, max_processes=None):
    """
        Факторизує список чисел паралельно.

        Args:
            *number: Список чисел.
            max_processes: Кількість процесів.

        Returns:
            Список чисел, на які числа з вхідного списку поділяються без залишку.
        """
    result = []

    # Визначення кількості ядер на машині
    num_cores = multiprocessing.cpu_count()

    # Визначення кількості процесів, що будуть запущені
    if max_processes is None or max_processes > num_cores:
        max_processes = num_cores

    with multiprocessing.Pool(processes=max_processes) as pool:
        result = pool.map(factorize_worker, number)

    return result


if __name__ == '__main__':
    start_time = time.time()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    stop_time = time.time()
    print(stop_time - start_time)  # 0.9099972248077393

    time.sleep(1)
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106,
                 1521580, 2130212, 2662765, 5325530, 10651060]
