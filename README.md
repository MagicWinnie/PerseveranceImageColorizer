# Parsing and combining channels of Perseverance Mars Rover
## Disclaimer
- ### As the same images but with different channels do not have similar filenames, the script uses scikit-image's `compare_ssim` which might not correctly find the correct images to merge with.  
- ### `combine.py` doesn't work. WIP  
## Requirements  
`python>=3.7`  
`pip3 install -r requirements.txt`  
## How to run  
`python3 parse.py -h`  
`python3 combine.py -h`
