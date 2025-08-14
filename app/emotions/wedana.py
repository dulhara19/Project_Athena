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


# option 2

# def calculate_pain(category):
#     category = category.lower()
#     if category == "mild":
#         return "Pain level: 1-3"
#     elif category == "moderate":
#         return "Pain level: 4-6"
#     elif category == "severe":
#         return "Pain level: 7-10"
#     else:
#         return "Invalid category. Choose mild, moderate, or severe."

# # Example usage:
# print(calculate_pain("mild"))

