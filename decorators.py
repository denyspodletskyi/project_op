def log_action(func):
    """
    Тут декоратор для логування дій
    """
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] Виконання {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
