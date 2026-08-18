import numpy as np
import cv2
import matplotlib.pyplot as plt

def print_coordinates_gaussian_kernel(x,y):
    matrix_of_tuples = np.dstack((x, y))
    #print(matrix_of_tuples)
    for row in matrix_of_tuples:
        print([tuple(pair) for pair in row])

def calculate_gaussian_kernel(size, sigma):
    """
    Calculate a Gaussian kernel manually.

    Parameters:
        size (int): The size of the kernel (must be odd).
        sigma (float): Standard deviation for Gaussian distribution.

    Returns:
        np.ndarray: Gaussian kernel matrix.
    """
    # Ensure size is odd
    if size % 2 == 0:
        raise ValueError("Kernel size must be odd.")

    # Define the range of values for the kernel
    k = size // 2
    x, y = np.meshgrid(np.arange(-k, k + 1), np.arange(-k, k + 1))

    print_coordinates_gaussian_kernel(x,y)

    # Calculate the Gaussian function for each coordinate
    kernel = (1 / (2 * np.pi * sigma**2)) * np.exp(-(x**2 + y**2) / (2 * sigma**2))

    # Normalize the kernel to ensure the sum is 1
    kernel /= np.sum(kernel)

    return kernel

# Example usage
size = 3  # Kernel size (e.g., 5x5)
sigma = 1      # Standard deviation for Gaussian

normalized_kernel = calculate_gaussian_kernel(size, sigma)
print("\nKernel Gaussian:")
print(normalized_kernel)

# Tạo Kernel Gaussian
kernel = cv2.getGaussianKernel(size, sigma)
gaussian_kernel = np.outer(kernel, kernel)  # Nhân ma trận để tạo kernel 2D

print("Kernel Gaussian:")
print(gaussian_kernel)

x, y = np.meshgrid(np.linspace(-2, 2, size), np.linspace(-2, 2, size)) 
# Create a figure and a 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the surface
ax.plot_surface(x, y, normalized_kernel, cmap='viridis')
ax.set_title('Gaussian Kernel')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Value')
plt.show()