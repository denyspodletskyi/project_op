def validate_value(value, sensor_type):
    """
    Проста валідація значень на основі типу сенсора
    """
    if sensor_type == "Температура":
        if -50 <= value <= 60:
            return value
    elif sensor_type == "CO2":
        if 0 <= value <= 5000:
            return value
    elif sensor_type == "Шум":
        if 0 <= value <= 150:
            return value
    elif sensor_type == "PM2.5":
        if 0 <= value <= 500:
            return value
    elif sensor_type == "Вологість":
        if 0 <= value <= 100:
            return value
    raise ValueError(f"Недопустиме значення для {sensor_type}: {value}")
