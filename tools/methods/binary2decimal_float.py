def binary2decimal_float(binary_str: str) -> float:
    #check it maybe not work properly
    """Convert a binary string representation to a decimal floating-point number."""
    binary_str = binary_str.strip()
    if binary_str.startswith('-'):
        return -binary2decimal_float(binary_str[1:])

    if '.' in binary_str:
        integer_part, fractional_part = binary_str.split('.')
    else:
        integer_part, fractional_part = binary_str, ''

    # Convert integer part
    decimal_integer = int(integer_part, 2) if integer_part else 0

    # Convert fractional part
    decimal_fraction = 0
    for i, bit in enumerate(fractional_part):
        decimal_fraction += int(bit) * (2 ** -(i + 1))

    return decimal_integer + decimal_fraction,step_by_step ,(0,0)