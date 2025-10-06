from random import gauss
from time import sleep

from utils import timed


@timed
def delayed_return(value, seconds=None, seconds_mean=1, seconds_sigma=0.25, verbose=False):
    """
    Sleep for a random or specified number of seconds, then return the given value.

    Parameters
    ----------
    value : any
        The value to return after sleeping.
    seconds : float or None, optional
        The number of seconds to sleep. If None, a random value is drawn from a normal
        distribution with mean `seconds_mean` and standard deviation `seconds_sigma`.
        Default is None.
    seconds_mean : float, optional
        Mean of the normal distribution for sleep time if `seconds` is None. Default is 1.
    seconds_sigma : float, optional
        Standard deviation of the normal distribution for sleep time if `seconds` is None. Default is 0.25.
    verbose : bool, optional
        If True, prints status messages. Default is False.

    Returns
    -------
    value : any
        The input value, returned after the delay.
    """
    def vprint(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    vprint(f"Starting with value: {value}")
    if seconds is None:
        seconds = gauss(seconds_mean, seconds_sigma)
    if seconds > 0:
        sleep(seconds)
    vprint(f"Returning: {value}")
    return value


@timed
def long_factorize(offset, base=100000001, verbose=False):
    """
    Find the greatest non-trivial factor pair of value = base + offset, eventually returning (1, value) if value is a
     prime number. This is done inefficiently factorization, in order to take up CPU time.

    Parameters
    ----------
    offset : int
        The offset to add to the base value to form the target integer.
    base : int, optional
        The base value to which the offset is added. Default is 100000001.
    verbose : bool, optional
        If True, prints status messages. Default is False.

    Returns
    -------
    value : int
        The integer being factorized (base + offset).
    f1 : int
        The first factor found (largest factor less than value).
    f2 : int
        The second factor found (value divided by f1).
    """
    def vprint(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    value = base + offset
    vprint(f"Finding factors of {base} + {offset} = {value}")
    next_guess = int(value / 2)
    while next_guess > 1 and (value % next_guess):
        next_guess -= 1
    f1 = next_guess
    f2 = value // next_guess
    vprint(f"{f1 * f2} = {f1} * {f2}")
    return value, f1, f2
