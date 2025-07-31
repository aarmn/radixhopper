import functools
import sys
import warnings


def deprecated(reason):
    if sys.version_info >= (3, 13):
        # Use the built-in deprecated decorator for Python 3.13+
        from warnings import deprecated as builtin_deprecated
        return builtin_deprecated(reason=reason)
    else:
        # Custom implementation for earlier Python versions
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                warnings.warn(f"{func.__name__} is deprecated. {reason}",
                              category=DeprecationWarning,
                              stacklevel=2)
                return func(*args, **kwargs)
            return wrapper
        return decorator
