## box

`box` is (yet another) file format for storing scientific data like 3D/2D simulation time series output. The motivation is to have a simple, robust, and portable alternative to HDF5.

![box logo](box.png)


### Architecture

In the end of the day, we want to store data hierarchically, and there is already a hierarchy we all familiar with - the filesystem hierarchy. We also want to have multiple data pieces together as one entity. For that, there are also ubiqutious archives.

Putting these two things together, we can have the relevant files organized to our discretion inside of a single archive file, and then operate on this file.

The main trick of the `box` file format is to use USTAR format for tar archives but without writing the trailing blocks, allowing it to be appendable at any moment. That is useful for simulations that continously write output data to disk. That also allows to recover the data with conventional tools more easily in case of corrupted writes.

Another trick is to make the tar archive randomly accessible without reading the entire file by compressing individual files. Most of the time, tar files are compressed as a whole, which requires one to first decompress the entire archive to even list the files. Transparent compression of individual files goes around that.

### Binary installation

1. Download and install the binary for your platform. To do it one go, run

```shell
curl -L -o box https://github.com/unkaktus/box/releases/latest/download/box-$(uname -s)-$(uname -m)
mkdir -p ~/bin
mv box ~/bin/
chmod +x ~/bin/box
```

Add `$HOME/bin` into your `$PATH` into your .bashrc:
```shell
export PATH="$HOME/bin:$PATH"
```


### Usage

By calling `box`, you can:
 * `append` files to a box
 * `absorb` (append and the remove) files to a box
 * `extract` box contents

### Installation of the ParaView plugin

1. Install Miniforge using the command below:

```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

2. Find the exact Python version your ParaView has. Go to ParaView->About ParaView and note down the "Python Library Version". For example, ParaView 5.13.1 has Python 3.10.13.

3. Create and activate the Mamba environment for `box` with the matching Python version and dependencies:

```shell
mamba create -y -n box python=3.10.13 zstandard
mamba activate box
```
4. From the `box` directory root, start ParaView via `box-pv` script by specifying path to your ParaView binary, 

```shell
./box-pv /path/to/paraview
```

or the application in case of macOS:

```shell
./box-pv /Applications/ParaView-5.13.1.app
```

That will start the ParaView and load all `box` plugins.

5. Now you are ready to open your `.box` files and make great movies.
