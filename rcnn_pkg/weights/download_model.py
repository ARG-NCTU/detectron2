from zipfile import ZipFile
import os
import gdown

# Download model03999.pth from google drive
dataset_url = 'https://drive.google.com/uc?export=download&id=1WIQ4Lp5ihJk1qQp5ABUP-8krWs2SIBl6'
dataset_name = 'brandname_model.pth'
if not os.path.isdir(dataset_name):
    gdown.download(dataset_url, output=dataset_name, quiet=False)


print("Finished downloading dataset.")