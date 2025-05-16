def validate_value(value, sensor_type):
    """
    Тут проста валідація значень на основі типу сенсора
    """
    if sensor_type == "Температура":
        if -50 <= value <= 60:
            return value
    elif sensor_type == "CO2":
        if 0 <= value <= 5000:
            return value
    elif sensor_type == "PM2.5":
        if 0 <= value <= 500:
            return value
    elif sensor_type == "Вологість":
        if 0 <= value <= 100:
            return value
    raise ValueError(f"Недопустиме значення для {sensor_type}: {value}")

def verify_reports(collector_data, saved_data):
    """
    Тут перевіряється, чи дані в звітах збігаються з зібраними даними.
    """
    for collected, saved in zip(collector_data, saved_data):
        if collected['type'] != saved['type']:
            return False
        if abs(collected['value'] - saved['value']) > 0.01:
            return False
        if collected['location'] != saved['location']:
            return False
    return True