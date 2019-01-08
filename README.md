# Nematode Egg Counting

This application reads an high resolution image file, extracts objects and
gets the total count of them.

## Environment Setup

- Download & Install [Python] using [Anaconda] or [Miniconda] (**Recommended**)

- Then you can run the following commands install required packages

  ```bash
  conda env create -f environment.yaml
  ```

*It is compatible with both Python 2.7 and Python 3.5, however installing Python 3.5 or greater is recommended.*

*It was tested on Windows and Mac OS X.*

## Usage

- Clone this repository and change directory

```bash
git clone https://github.com/ukalwa/nematode_egg_counting
cd nematode_egg_counting
# Activate the conda environment
activate egg_counting
```

*Configuration file `src/config.ini` contains all the settings for blob
identification, fig sizes and so on. Before running the script, update
accordingly.*

- To process a single file using file dialog GUI

  ```bash
  python run.py
  (or)
  python run.py -uf
  ```

- To process a directory full of image using file dialog GUI

  ```bash
  python run.py -ud
  ```

- To process a single file with its known absolute file path

  ```bash
  python run.py -f <file_path>
  ```

- To process a directory full of images with known path

  ```bash
  python run.py -d <dir_path>
  ```

- To process only some files in a directory with known path

  ```bash
  python run.py -d <dir_path> -p <pattern string>
  ```

## Steps involved

The code performs these following steps:

1. It extracts the configuration parameters related to blob identification, figure sizes, bounding box parameters and so on
2. Read the image file as a 3-d numpy array and splits it into various blocks and stores them as a list of numpy arrays.
3. It then loops though each block and detects any eggs based on parameters set in the config file and records the count and adds it to the total count
4. After all the blocks are completed, total egg counts, blocks with bounding boxes around eggs, egg params are all saved in text files for reference and debugging purposes

## Here are some snapshots

The one on the left is a block of the original image and the one on the right is the processed image with eggs identified and labelled with bounding boxes

### **Top layer**

![image1]

### **Interface layer**

![image2]

### **Bottom layer**

![image3]

## Documentation

For generating documentation, please follow these steps:

- Make sure you have sphinx installed, you can install it like this

```bash
pip install sphinx sphinx_rtd_theme
```

- Move to the docs directory and run make. It takes couple of minutes to generate the build files.

```bash
cd docs
make html
explorer build\html\index.html
```

## License

This code is GNU GENERAL PUBLIC LICENSED.

## Contributing

If you have any suggestions or identified bugs please feel free to post
them!

  [OpenCV 3.1.0]: http://opencv.org/downloads.html
  [Python]: https://www.python.org/downloads/
  [numpy]: https://www.scipy.org/scipylib/download.html
  [matplotlib]: https://matplotlib.org/
  [Anaconda]: https://www.anaconda.com/download/
  [Miniconda]: https://conda.io/miniconda.html
  [image1]: Images/Picture1.jpg
  [image2]: Images/Picture2.jpg
  [image3]: Images/Picture3.jpg
