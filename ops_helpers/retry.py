from functools import wraps


def retry_after_class_action(
    max_tries: int,
    error_type: Exception,
    corrective_method: str,
    ):         # noqa: F125

    """
    Decorator that can be applied to an instance method
    If instance method raises error, will take corrective action and re-run
    Will run no more than max_tries (including first try)
    Useful for: resetting an API token if the cached token fails; re-pinging unreliable APIs
    params:
        - max_tries must be 1 or more (or else function will never run)
        - error_type is the anticipated Exception subclass
            - unanticipated Exceptions will not be caught and will still raise an error
        - corrective_method must be name of a method in same class as the decorated method
            - method can be nested up to one level deep (useful if using class composition)

    Example usage (re-running code with random errors):
        from random import random
        class Adder():

            @retry_after_class_action(
                max_tries=10, error_type=ValueError, corrective_method='alert_to_error')
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
            if '.' in corrective_method:
                base, _, method = corrective_method.partition('.')
                corrective_action = getattr(getattr(self, base), method)
            else:
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
