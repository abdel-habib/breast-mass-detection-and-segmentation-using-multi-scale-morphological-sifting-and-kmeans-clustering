# <h1 align="center">Mammogram Mass Detection and Segmentation using Multi-scale Morphological Sifting and K-means Clustering</h1>


![alt text](https://github.com/abdalrhmanu/mammographic-breast-mass-detection-and-segmentation/blob/main/report/report_images/visualize_segmentation/segmentation_results_cropped.png?raw=true)

Setup Environment Locally
============

To set up a virtual environment, follow the procedure found in <a href="https://github.com/abdalrhmanu/mammogram-mass-detection/blob/main/env.setup.md" target="_blank"> `env.setup.md`</a>.

Directory Structure
============

```
.
├── dataset             # Holds the project dataset folders and files.
    ├── groundtruth     # Ground truth dataset files.
    ├── images          # Dataset images files.
    ├── masks           # Dataset masks files.
    ├── overlay         # Dataset overlay files.
    ├── all.txt         # All images names stored in a .txt file.
    ├── negatives.txt   # All negative labelled images names stored in a .txt file.
    └── positives.txt   # All positive labelled images names stored in a .txt file.
├── literature          # Documentation/paper/project description, etc..
├── helpers             # Some developed packages and modules.
└── notebooks           # Jupyter notebooks used for development.

```

Dataset Setup
============

The dataset folder structure is uploaded in this repository without any of the images. Thus, the dataset folder (from project drive) has to be downloaded and the folders inside has to be moved to this repository folder (inside the dataset root folder). 
