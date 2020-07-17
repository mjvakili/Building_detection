# Dataset Structure

The project data needs to be *structured* as specified in this document.

All the *data* should be placed within the `data` folder. (i.e. `./data`)

Each **dataset** should be placed in a subfolder under `data` with a unique name. (e.g. `./data/xview`)

Each *dataset* should have **four subfolders** within,

- `train` containing the images from which the model will *learn* to identify damage. (typically 80% of all labelled data) (i.e. `./data/xview/train`)
- `validation` containing the images which will be used to *tune* the model. (typically 10% of all labelled data) (i.e. `./data/xview/validation`)
- `test` containing the images which will be used to *score* the model. (typically 10% of all labelled data) (i.e. `./data/xview/test`)

Each *subfolder* is split into **two folders**,

- `images` containing the images of the region **before the disaster**. (i.e. `./data/xview/test/images`)
- `labels` containing the label masks (containing the building polygons) corresponding to the images. (i.e. `./data/xview/test/labels`)
- The dataloader as defined by neat-EO requires a `[0-9]*/[0-9]*/[0-9]*` directory structure within the `images` and `labels` directories to load in the images and labels. The matching image and label files should have the *same filename*. For example, the image  `./data/xview/train/images/1/10/000000032.png` corresponds to the label `./data/xview/train/labels/1/10/000000032.png`. 


