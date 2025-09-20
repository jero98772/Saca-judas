def decimal2binary_float(num: float, precision: int = 10) -> str:
    """Convert a decimal floating-point number to binary string representation."""
    if num < 0:
        return '-' + decimal2binary_float(-num, precision),step_by_step ,(0,0)

    integer_part = int(num)
    decimal_part = num - integer_part

    # Convert integer part to binary
    binary_integer = bin(integer_part)[2:]

    # Convert decimal part to binary
    binary_decimal = []
    count = 0
    while decimal_part and count < precision:
        decimal_part *= 2
        bit = int(decimal_part)
        binary_decimal.append(str(bit))
        decimal_part -= bit
        count += 1

    if binary_decimal:
        return f"{binary_integer}.{''.join(binary_decimal)}",step_by_step ,(0,0)
    else:
        return binary_integer,step_by_step ,(0,0)