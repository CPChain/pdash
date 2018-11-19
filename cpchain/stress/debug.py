def functrace(func):
    def newfunc(*args, **kwargs):
        print(func.__name__)
        ret = func(*args, **kwargs)
        return ret
    return newfunc
