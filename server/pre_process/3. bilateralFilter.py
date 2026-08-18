import numpy as np
import cv2
from matplotlib import pyplot as plt

def bilateral_filter(image, diameter, sigma_color, sigma_space):
    # Check if the image is grayscale or color
    is_color = len(image.shape) == 3
    if not is_color:
        image = image[:, :, np.newaxis]  # Convert grayscale to single channel for uniform processing
    
    # Get image dimensions
    height, width, channels = image.shape
    
    # Create an output image
    output = np.zeros_like(image, dtype=np.float32)
    
    # Calculate the radius of the kernel
    radius = diameter // 2
    
    # Precompute the spatial weights (Gaussian function for spatial distances)
    spatial_weights = np.zeros((diameter, diameter), dtype=np.float32)
    for i in range(diameter):
        for j in range(diameter):
            x, y = i - radius, j - radius
            spatial_weights[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma_space**2))
    
    # Normalize spatial weights
    spatial_weights /= spatial_weights.sum()
    
    # Apply the filter to each channel
    for c in range(channels):
        for y in range(radius, height - radius):
            for x in range(radius, width - radius):
                # Extract the local region
                local_region = image[y-radius:y+radius+1, x-radius:x+radius+1, c]
                
                # Calculate intensity weights (Gaussian function for intensity differences)
                intensity_weights = np.exp(-((local_region - image[y, x, c])**2) / (2 * sigma_color**2))
                
                # Combine spatial and intensity weights
                combined_weights = spatial_weights * intensity_weights
                
                # Normalize the combined weights
                combined_weights /= combined_weights.sum()
                
                # Compute the filtered value for the current pixel
                output[y, x, c] = np.sum(combined_weights * local_region)
    
    # Clip values to the valid range [0, 255] and convert to uint8
    output = np.clip(output, 0, 255).astype(np.uint8)
    
    # Return the result for grayscale images without the added channel
    return output.squeeze() if not is_color else output

# Load an example image
image = cv2.imread(r'./img/bilateral_example_image.jpg')

# Apply the custom bilateral filter
filtered_image = bilateral_filter(image, diameter=15, sigma_color=75, sigma_space=75)

# Apply OpenCV bilateral filter for comparison
opencv_filtered_image = cv2.bilateralFilter(image, d=15, sigmaColor=75, sigmaSpace=75)

# Display the results
plt.figure(figsize=(10, 5))
plt.subplot(131), plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), plt.title('Original Image')
plt.xticks([]), plt.yticks([])
plt.subplot(132), plt.imshow(cv2.cvtColor(opencv_filtered_image, cv2.COLOR_BGR2RGB)), plt.title('OpenCV Bilateral Filter')
plt.xticks([]), plt.yticks([])
plt.subplot(133), plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)), plt.title('Custom Bilateral Filter')
plt.xticks([]), plt.yticks([])
plt.show()
