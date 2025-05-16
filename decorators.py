def log_action(func):
    """
    Тут декоратор для логування дій
    """
    def wrapper(*args, **kwargs):
        print(f"Почекайте, йде виконання {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
