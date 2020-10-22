echo "installing rasterio"
pip3 install --user rasterio

echo "creating place-holders for the raw and processed files"
RAW_DATA_DIR=DATA/raw
INTER_DATA_DIR=DATA/interim
PROCESSED_DATA_DIR=DATA/processed

mkdir -p $RAW_DATA_DIR
mkdir -p $INTER_DATA_DIR
mkdir -p $PROCESSED_DATA_DIR

echo "Downloading the test mosaic file"
wget https://raw.githubusercontent.com/drivendataorg/open-cities-ai-challenge/master/1st%20Place/data/processed/test_mosaic.csv 

echo "Downloading the test data"
wget https://drivendata-public-assets.s3.amazonaws.com/test.tgz

mv test.tgz $RAW_DATA_DIR

mv test_mosaic.csv $PROCESSED_DATA_DIR

echo "Extracting test files..."
tar -xvzf $RAW_DATA_DIR/test.tgz -C $INTER_DATA_DIR


echo "Stitching test files..."
python3 -m preprocessor.stitch_test \
    --df_path=$PROCESSED_DATA_DIR/test_mosaic.csv \
    --path_pattern=$INTER_DATA_DIR/test/*/*.tif \
    --dst_dir=$PROCESSED_DATA_DIR/test
