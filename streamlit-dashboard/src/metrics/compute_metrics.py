# compute the average temperature across the entire raw dataset
def calculate_average_temperature(data) -> float:
    if data is None or len(data) == 0:
        return 0
    total_temp = data['mean_temp_k'].sum()
    return total_temp / len(data)

# compute the median temperature from the dataset
def calculate_median_temperature(data) -> float:
    if data is None or len(data) == 0:
        return 0
    return float(data['mean_temp_k'].median())

# compute the number of high temperature events above a certain threshold
def count_high_temp_events(data, threshold=400) -> int:
    if data is None or len(data) == 0:
        return 0
    return int((data['mean_temp_k'] > threshold).sum())

# compute the total number of unique entries in the dataset
def calculate_number_of_events(data) -> int:
    if data is None or len(data) == 0:
        return 0
    return int(len(data.drop_duplicates()))
