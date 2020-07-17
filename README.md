# Automated Building Detection using Neat-EO.pink
Below steps describe the initial tests with Neat-EO.pink.


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
python neat-eo preprocess_xview.py [--config] [--crop]

```
The above command will create the dataset as per the specifications.
