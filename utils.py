import concurrent.futures
from functools import partial, wraps
from time import time


def timed(f):
    """
    Decorator to measure the execution time of a function.

    Parameters
    ----------
    f : callable
        The function whose execution time is to be measured.

    Returns
    -------
    callable
        A wrapped function that returns a tuple (result, elapsed_time), where
        `result` is the output of the original function and `elapsed_time` is
        the time taken in seconds.
    """
    @wraps(f)
    def f_timed(*args, **kwargs):
        t0 = time()
        result = f(*args, **kwargs)
        t = time() - t0
        return result, t

    return f_timed


@timed
def submit_get_results(timed_fun, n, pool_type, as_completed=False, max_workers=None, verbose=False):
    """
    Run a function across a pool of workers using submit, collecting results and execution times.

    Parameters
    ----------
    timed_fun : callable
        A function that accepts an integer and returns a tuple (result, exec_time).
    n : int
        Number of tasks to submit to the pool.
    pool_type : concurrent.futures.Executor
        The executor class to use (e.g., ThreadPoolExecutor or ProcessPoolExecutor).
    as_completed : bool, optional
        If True, results are collected as tasks complete. If False, results are collected in submission order.
        Default is False.
    max_workers : int or None, optional
        The maximum number of workers for the pool. If None, the default for the executor is used.
    verbose : bool, optional
        If True, enables verbose output for the timed function. Default is False.

    Returns
    -------
    results : list
        List of results returned by `timed_fun`.
    times : list of float
        List of execution times for each task.
    """
    with pool_type(max_workers) as pool:
        tasks = []
        pfun = partial(timed_fun, verbose=verbose)
        for i in range(n):
            tasks.append(pool.submit(pfun, i))
        if as_completed:
            results_times = [task.result() for task in concurrent.futures.as_completed(tasks)]
        else:
            results_times = [task.result() for task in tasks]
        results, times = zip(*results_times)
        return results, times


@timed
def map_results(timed_fun, n, pool_type, max_workers=None, verbose=False):
    """
    Run a function across a pool of workers using map, collecting results and execution times.

    Parameters
    ----------
    timed_fun : callable
        A function that accepts an integer and returns a tuple (result, exec_time).
    n : int
        Number of tasks to map across the pool.
    pool_type : concurrent.futures.Executor
        The executor class to use (e.g., ThreadPoolExecutor or ProcessPoolExecutor).
    max_workers : int or None, optional
        The maximum number of workers for the pool. If None, the default for the executor is used.
    verbose : bool, optional
        If True, enables verbose output for the timed function. Default is False.

    Returns
    -------
    results : list
        List of results returned by `timed_fun`.
    times : list of float
        List of execution times for each task.
    """
    with pool_type(max_workers) as pool:
        pfun = partial(timed_fun, verbose=verbose)
        results_times = pool.map(pfun, range(n))
        results, times = zip(*results_times)
        return results, times


def display_results(timed_fun, n, pool_type, submit_type, as_completed=False, max_workers=None, verbose=False):
    """
    Display results and timing information for running a function in a pool.

    Parameters
    ----------
    timed_fun : callable
        The function to run in the pool.
    n : int
        Number of tasks to run.
    pool_type : concurrent.futures.Executor
        The executor class to use (e.g., ThreadPoolExecutor or ProcessPoolExecutor).
    submit_type : {'submit', 'map'}
        The method to use for submitting tasks to the pool.
    as_completed : bool, optional
        If True and `submit_type` is 'submit', results are collected as tasks complete. Default is False.
    max_workers : int or None, optional
        The maximum number of workers for the pool. If None, the default for the executor is used.
    verbose : bool, optional
        If True, enables verbose output for the timed function. Default is False.

    Returns
    -------
    None
    """
    print(f"Running: {timed_fun.__name__}")
    if submit_type == 'submit':
        (results, times), total_time = submit_get_results(timed_fun, n, pool_type, as_completed=as_completed,
                                                          max_workers=max_workers, verbose=verbose)
    elif submit_type == 'map':
        (results, times), total_time = map_results(timed_fun, n, pool_type, max_workers=max_workers, verbose=verbose)
    else:
        raise ValueError(f"Unrecognized value for submit_type: {submit_type}")
    print(f"Results: {results}")
    print(f"Task times: {' + '.join(f'{t:.3g}' for t in times)} = {sum(times):.3g}")
    print(f"Actual time: {total_time}")
