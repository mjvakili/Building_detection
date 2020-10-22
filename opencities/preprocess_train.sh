echo "Installing the necessary libraries"
conda install -c conda-forge gdal
pip install aeronet --user

echo "creating place-holders for the raw and processed files"

RAW_DATA_DIR=DATA/raw
INTER_DATA_DIR=DATA/interim
PROCESSED_DATA_DIR=DATA/processed

echo "Downloading the train tier 1 data"
wget https://drivendata-public-assets-eu.s3.eu-central-1.amazonaws.com/train_tier_1.tgz

mv train_tier_1.tgz $RAW_DATA_DIR

echo "Extracting train tier 1 files..."
tar -xvzf $RAW_DATA_DIR/train_tier_1.tgz -C $INTER_DATA_DIR


# resample train data to 0.1 meters per pixel
echo "Resamping train data to 0.1 m/pixel"
python3 -m preprocessor.resample --path_pattern=$INTER_DATA_DIR/train_tier_1/*/*/*.tif --dst_res=0.1

# for each resampled tif file create raster mask from provided geometries in .geojson file
echo "Creating raster masks"
python3 -m preprocessor.generate_masks --path_pattern=$INTER_DATA_DIR/train_tier_1/*/*/res-*.tif

# slicing big tif files to small ones with size 1024x1024
echo "Slicing tif files..."
python3 -m preprocessor.cut_train \
    --path_pattern=$INTER_DATA_DIR/train_tier_1/*/*/res-*.tif \
    --dst_dir=$PROCESSED_DATA_DIR/train \
    --sample_size=1024
