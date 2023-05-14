import sys
sys.path.append('..\\helpers')

import cv2
import os
import numpy as np
import math

from functools import reduce
from pywt import dwt2
from tqdm import tqdm, tqdm_notebook

# From helpers directory
import display

from sklearn.cluster import KMeans
import warnings

class Segmentation:
    def __init__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)


    def mean_shift_filter(self, image, spatial_radius, range_radius):
        """
        Apply mean shift filter to a grayscale image.

        Parameters:
        - image: 2D numpy array of type uint16 with shape (height, width)
        - spatial_radius: int, spatial distance (in pixels) to consider for the filter
        - range_radius: int, color distance to consider for the filter

        Returns:
        - filtered_image: 2D numpy array of type uint16 with shape (height, width),
                        the result of the filter
        """

        # Convert image to float32 for better precision
        image_float = image.astype(np.float32)

        # Convert image to uint8 for OpenCV
        image_uint8 = cv2.convertScaleAbs(image_float / np.max(image_float) * 255)

        # Convert 2-channel grayscale image to 3-channel grayscale image
        image_3ch = cv2.cvtColor(image_uint8, cv2.COLOR_GRAY2BGR)

        # Apply mean shift filter using OpenCV
        filtered_image_uint8 = cv2.pyrMeanShiftFiltering(image_3ch, spatial_radius, range_radius)

        # Convert the filtered image back to uint16
        filtered_image_float = cv2.cvtColor(filtered_image_uint8, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0 * np.max(image_float)
        filtered_image = filtered_image_float.astype(np.uint16)

        return filtered_image
    
    def eliminate_by_area(self, image, min_area, max_area):
        # Convert to uint8
        image = (image / np.max(image) * 255).astype(np.uint8)
        
        # Apply mean shift filtering to enhance tumor features
        filtered = self.mean_shift_filter(image, spatial_radius=45, range_radius=60)

        # Normalize the filtered image to improve contrast
        normalized_image = cv2.normalize(filtered, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Apply thresholding
        # _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.adaptiveThreshold(normalized_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 9, 2)

        # Perform morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel), cv2.MORPH_OPEN, kernel)

        # Find contours of thresholded image
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create a blank image to draw contours on
        result = np.zeros_like(opened)

        # Loop through contours and eliminate those outside the desired area range
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if min_area < area < max_area:
                cv2.drawContours(result, [cnt], 0, (255, 255, 255), -1)
                
        # remove any lines resulted from the contours by performing morphological opening to remove lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        
        result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)

        return result

    def slico(self, img):
        # Apply Superpixel SLIC algorithm
        algo = cv2.ximgproc.createSuperpixelSLIC(img, cv2.ximgproc.SLICO, 10)
        algo.iterate(10)

        # Get labels and number of superpixels
        labels = algo.getLabels()
        num_superpixels = algo.getNumberOfSuperpixels()

        # Calculate superpixel means
        superpixel_means = np.zeros((num_superpixels, 3))
        for k in range(num_superpixels):
            mask = (labels == k).astype('uint8')
            superpixel_means[k] = cv2.mean(img, mask)[:3]

        # Calculate superpixel areas
        # superpixel_areas = np.bincount(labels.flatten())

        return superpixel_means, num_superpixels, labels
    

    def kmeans (self, img):

        superpixel_means, num_superpixels, labels = self.slico(img)

        # Perform k-means clustering on the superpixel means
        kmeans = KMeans(n_clusters=3)  # Replace K with the desired number of clusters
        kmeans.fit(superpixel_means)
        cluster_labels = kmeans.labels_

        # Replace original image pixels with cluster means
        img_clustered = img.copy()
        for k in range(num_superpixels):
            mask = (labels == k).astype('uint8')
            cluster_label = cluster_labels[k]
            cluster_mean = kmeans.cluster_centers_[cluster_label]

            img_clustered[mask > 0] = cluster_mean

        # Binarize the clustered region images using thresholding
        gray_clustered = cv2.cvtColor(img_clustered, cv2.COLOR_BGR2GRAY)

        _, binary_image = cv2.threshold(gray_clustered, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return binary_image


