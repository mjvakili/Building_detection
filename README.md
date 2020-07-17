# Automated Building Detection using Neat-EO.pink

## Network & setup
Network details and how to setup can be found here: https://neat-eo.pink. Advised to walk through the tutorial.

## Dataset - xView2 Challenge

##### 1. Download raw dataset:
The xView2 dataset can be downloaded from https://xview2.org/dataset (login required).

##### 2. Extract raw dataset:

Extract the contents of the downloaded .tar file:

```
tar -xvzf <file.tar>
```
Place the extracted 'images' and 'labels' folders in the 'data/xview' folder. For training and testing the model all data releases are combined.

##### 3. Create Training Datset:

The training dataset can be created by executing the following command:

```
python neat-eo/preprocess_xview.py --config ../config.toml --crop 512 512
```
The above command will create the dataset as per the specifications and splits the 1024 x 1024 images into four 512 x 512 images. 

##### Configuration:

`sint_maarten_2017.py` accepts the command line arguments described below,

```
usage: preprocess_xview.py [-h] --config CONFIG --crop WIDTH HEIGHT 


optional arguments:
  -h, --help            Show this help message and exit (NEEDS TO BE ADDED)
  --config CONFIG       Path to config file
  --crop                Crops image into smaller images of specified width and height 
                        (significantly increases processing time)
```

## Initial results

##### Model: 
https://rodekruis.sharepoint.com/sites/510-Team/Gedeelde%20%20documenten/%5BPRJ%5D%20Automated%20Damage%20Assessment/Automated%20Building%20Detection/pth/checkpoint-00050-training-11012020.pth

##### Trained on:
`train.tar`as downloaded from https://xview2.org/dataset

##### Tested on:
Images corresponding to nepal-flooding disaster which were not part of `train.tar`. 

##### Initial Results_:

Mean IOU: 0.6927478022575819



## Next steps


