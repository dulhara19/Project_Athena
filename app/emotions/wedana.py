def calculate_pain(level):
    if not (1 <= level <= 10):
        return "Invalid pain level. Please enter a number between 1 and 10."
    
    if 1 <= level <= 3:
        return "mild"
    elif 4 <= level <= 6:
        return "moderate"
    else:
        return "severe"

# Example usage:
print(calculate_pain(2))  # mild
print(calculate_pain(5))  # moderate
print(calculate_pain(9))  # severe



s