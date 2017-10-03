'''
Author              : Saidhon Orifov
Program             : Use Otsu's method to determine the best threshold speed
                      to start giviing out tickets.
Last Modified by    : Saidhon Orifov (09/17/17)
'''

import matplotlib.pyplot as plt
import numpy as np
import csv
import math

'''
Otsu's Brute Force Method
Use Weighted Variance formula to get the best threshold

@:param all_thresholds - data collected from csv file, essentially sorted speed data
@:returns best_threshold - best threshold to start giving tickets at
'''
def otsu_method(all_thresholds):
    # Initialize an empty array to store all variance values
    all_variances           = []

    # Set the best mixed variance to infinity
    best_mixed_variance     = np.inf

    # Even though best threshold is supposed to be a NaN, initialize it to infinity
    best_threshold          = np.nan

    # Evaluate the clustering using the weighted sum of the two variances
    for threshold_index in range(0, len(all_thresholds)):
        wt_under    = float(len(all_thresholds[0:threshold_index])/len(all_thresholds))
        var_under   = np.var(all_thresholds[0:threshold_index])
        wt_over     = float(len(all_thresholds[threshold_index:-1])/len(all_thresholds))
        var_over    = np.var(all_thresholds[threshold_index:-1])

        # Compute mixed variance using Wl, Wr, variance for the left cluster, and variance for the right cluster
        mixed_variance = (wt_under * var_under) + (wt_over * var_over)

        # keep track of all variances which will be reused for a plot vs all thresholds
        all_variances.append(mixed_variance)

        # Check if current mixed variance is less than the current best variance
        # If it is less, then new best threshold is threshold at current index
        if mixed_variance < best_mixed_variance:
            best_mixed_variance = mixed_variance
            best_threshold      = all_thresholds[threshold_index]

    return best_threshold, best_mixed_variance, all_variances

'''
Use the given speed data to quantize data it into 2 mph bins

This function declrease two different data structures - an array and a dictionary
1)  Dictionary is used to filter each speed value in the provided data into its own bin using range() function.
    Each key value which is essentialy a subarray is then stored into the storage, where all bins go.
2)  The final array that contains data about all bins, will be used to create a histogram.

@:param   speed_data - data to be used to quantize into bins
@:returns array containing sub arrays which are bins that hold values in 2mph range
'''
def quantize_to_bins(speed_data):
    # Initialize a storage for a total number of 2 mph range bins
    total_bins_dict      = {}
    total_bins           = []

    # Determine the minimum and maximum speed range to be able to quantize data
    # effectively.  For example 41.4 mph would fall into categorie of ranges between 40 and 42 mph
    min_speed_range = math.floor(speed_data[0])  if (math.floor(speed_data[0]) % 2.0 == 0) else math.floor(speed_data[0] - 1)    # min speed range
    max_speed_range = math.floor(speed_data[-1]) if (math.floor(speed_data[-1]) % 2.0 == 0) else math.floor(speed_data[-1] + 1)  # max speed range

    # Determine the number of bins we need to quantize the data by dividing the difference
    # between the (max, min) by 2 => difference(max_range, min_range)/2
    bins_count = (max_speed_range - min_speed_range)/2

    # Create a copy of min speed range in order to use for iteration and store 2 mph range dictionary keys
    base_speed_range             = min_speed_range

    # Loop until bin speed range reaches the max range and store 2 mph range keys
    # Create an empty array for each key range
    while (base_speed_range < max_speed_range):
        # Create a key, whos value is an empty array
        total_bins_dict[range(base_speed_range, base_speed_range+2)] = []

        # Increment the current min speed range
        base_speed_range += 2

    # Store each speed value into its own bin
    for speed_value in speed_data:
        current_speed_value_min_range = math.floor(speed_value) if math.floor(speed_value) % 2 == 0 else math.floor(speed_value - 1)

        # Add the speed value that belongs to its range
        key = range(current_speed_value_min_range, current_speed_value_min_range + 2)
        total_bins_dict.get(key).append(speed_value)

    # Reset the base speed range
    base_speed_range = min_speed_range

    # Store the value for each key into an array which essentially will have total number of bins or subarrays
    while (base_speed_range < max_speed_range):
        bin = total_bins_dict.get(range(base_speed_range, base_speed_range+2))
        total_bins.append(bin)
        base_speed_range += 2

    return total_bins, min_speed_range

'''
Reads the CSV file, retreives the speed elements from and puts it into an array

Use csv module to open the file, read and save the speeds in the file
@:param filename - file string that will be used to open it
@:returns - data containing all speeds
@:rtype - array
'''
def fetch_data(filename):
    # Initialize a storage to hold the data
    speed_data = []

    # Open the file using filename string
    with open(filename, 'r') as datafile:
        speed_data_reader = csv.reader(datafile)
        for temp_speed_array in speed_data_reader:
            speed_data.append(float(temp_speed_array[0]))

    return speed_data

'''
Plot the quantized data to get a visualization of clustering
@:param total_bins - an array that consists of bins or subarrays that fall within 2 mph range
@:param min_speed_range - the minimum speed to start the plot of the first bin with
'''
def plot_data(total_bins, min_speed_range):
    fig1 = plt.figure(1)
    plt.xlabel('Speed [mph]')
    plt.ylabel('Frequency')
    plt.title('Histogram of Speeds (bins of 2 mph)')
    for bin in total_bins:
        plt.hist(bin, bins=[min_speed_range, min_speed_range + 2], edgecolor='black', color='blue')
        min_speed_range += 2

    plt.show()

'''
Plots all possible thresholds vs all variances determined using Otsu's method
The result of the plot should tell, where the graph hits the low, and that is
where the threshold should be and that is where the data is divided into 2 clusters
'''
def plot_thresholds_vs_variances(all_thresholds, all_variances):
    fig2 = plt.figure(2)
    plt.xlabel('Threshold [mph]')
    plt.ylabel('Weighted Variance')
    plt.title('Threshold vs Mixed Variance')
    plt.plot(all_thresholds, all_variances, '.')
    plt.grid(True)

    plt.show()


'''
Main function that executes the program in the order
'''
def main():
    # Get data from CSV file and store it
    speed_data = fetch_data("speed_data.csv")

    # Sort the data in order to be able to obtain min and ax
    speed_data.sort()

    # Quantize Data into bins
    total_bins, min_speed_range = quantize_to_bins(speed_data)

    # Plot a histogram of total bins
    plot_data(total_bins, min_speed_range)

    # Retreive best threshold and best mixed variance using otsus method
    threshold, best_mixed_variance, all_variances = otsu_method(speed_data)

    # Plot all threshold values vs all variances observed for each threshold
    plot_thresholds_vs_variances(speed_data, all_variances)



if __name__ == "__main__":
    main()
