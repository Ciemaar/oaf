to_qa = []


def qa(func):
    to_qa.append(func.__name__)

    def wrapper(*args, **kwargs):
        warnings.warn("non QA'd code called")
        return func(*args, **kwargs)

    return wrapper
