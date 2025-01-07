import os
import pickle
import matplotlib.pyplot as plt

def plot_processed_file(file_path, title="Climate Data Visualization"):
    """
    Loads a .pickle file and plots the data as a scatter plot.
    
    Parameters:
        file_path (str): Path to the .pickle file to load.
        title (str): Title of the plot.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Load the pickle file
    with open(file_path, 'rb') as f:
        data = pickle.load(f)

    positions = data.get("positions", [])
    colors = data.get("colors", [])

    # Ensure the positions array has valid x, y pairs
    if len(positions) % 2 != 0:
        print("Error: Positions data is not a multiple of 2.")
        return

    # Reshape positions into (x, y) pairs
    x_coords = positions[0::2]
    y_coords = positions[1::2]

    # Normalize colors for visualization
    rgba_colors = [(r / 255, g / 255, b / 255, a / 255) for r, g, b, a in zip(*[iter(colors)] * 4)]

    # Create scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(x_coords, y_coords, c=rgba_colors, s=5, edgecolor='none')
    plt.title(title)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.axis("equal")
    plt.grid(True)
    plt.show()

# Example usage
if __name__ == "__main__":
    # processed_file = "../processed_files/tmin_1980.pickle"
    # plot_processed_file(processed_file, title="Minimum Temperature Data")

    processed_file = "../processed_files/prcp_1980.pickle"
    plot_processed_file(processed_file, title="Annual Daily Precipitation")
