from functools import wraps


def retry_after_class_action(
    max_tries: int,
    corrective_method: callable,
    error_type: Exception):         # noqa: F125

    """
    Decorator that can be applied to an instance method
    If instance method raises error, will take corrective action and re-run
    Will run no more than max_tries (including first try)
    Useful for resetting an API token if the cached token fails
    params:
        - max_tries must be 1 or more
        - corrective_method must be a method in same class as the decorated method
        - error_type must be the anticipated Exception subclass

    Example usage:
        from random import random
        class Adder():

            @retry_after_class_action(
                max_tries=10, corrective_method='alert_to_error', error_type=ValueError)
            def add_two_sometimes(self, a, b):
                if random() <= .5:
                    raise ValueError('Not working')
                return a + b

            def alert_to_error(self):
                print('Hit a snag, trying again!')

    """
    def _retry(func):
        @wraps(func)
        def wrap(self, *arg, **kwargs):
            corrective_action = getattr(self, corrective_method)
            for _ in range(max_tries):
                try:
                    result = func(self, *arg, **kwargs)
                except error_type:
                    corrective_action()
                    continue
                else:
                    break
            else:
                raise StopIteration(
                    f'Function still failed after {max_tries} attempts')
            return result
        return wrap
    return _retry
