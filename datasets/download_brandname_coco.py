from zipfile import ZipFile
import os
import gdown

dataset_url = 'https://drive.google.com/uc?export=download&id=144ALeukpsHLPJhVVgkHY5NrT3dhyLDxJ'
dataset_name = 'brandname_cocoformat'
if not os.path.isdir(dataset_name):
    gdown.download(dataset_url, output=dataset_name + '.zip', quiet=False)
    zip1 = ZipFile(dataset_name + '.zip')
    zip1.extractall(dataset_name)
    zip1.close()

print("Finished downloading dataset.")