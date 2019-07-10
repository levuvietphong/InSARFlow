<p align="left">
<img src="logo.png" alt="" width="500"/>
</p>
Parallel InSAR processing for time-series analysis 

## Introduction
As [Interferometric Synthetic Aperture Radar (InSAR)](https://en.wikipedia.org/wiki/Interferometric_synthetic-aperture_radar) data becomes increasingly popular, the ability to process these large datasets for time-series analysis is important.
InSarFlow utilizes [mpi4py](https://pypi.org/project/mpi4py/) for parallel processing of SAR interferograms and time-series analysis based on [ISCE](https://winsar.unavco.org/software/isce) and [GIAnT](http://earthdef.caltech.edu/projects/giant/wiki#) models.

InSarFlow has the following features:

- **Automatic downloading** SAR data from [Alaska Satellite Facility (ASF)](https://vertex.daac.asf.alaska.edu/).
- **Parallel processing** of interferograms. Because ISCE processing for each interferogram is independent, running ISCE for many pairs can be implemented very efficiently in parallel. Using [Message Passing Interface (MPI)](https://en.wikipedia.org/wiki/Message_Passing_Interface), InSarFlow supports large-scale processing on clusters and supercomputers.

## Prerequisite

The following packages are required for running InSarFlow:

* [ISCE 2.2.0](https://winsar.unavco.org/software/isce) (See [here](https://github.com/scottyhq/isce_notes/tree/master/Ubuntu) for installation instruction)
* [GIAnT](http://earthdef.caltech.edu/projects/giant/wiki#)
* [mpi4py](https://pypi.org/project/mpi4py/)
* [networkX](https://networkx.github.io/)
* [pandas](https://pandas.pydata.org/)


## Installation
Download and extract the code (name it InSarFlow) to your home folder. Add the following to your .bashrc file:
```bash
export PATH=$PATH:/home/USERNAME/InSarFlow/scripts
```

I setup ISCE and GIAnT in 2 separate environments.
For ISCE and GIAnT to recognize InSarFlow, add InSarFlow/scripts folder to the PYTHONPATH of each environment

* ISCE config
```bash
export InSarFlow_HOME=/home/USERNAME/InSarFlow
export PYTHONPATH=$ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component:$InSarFlow_HOME/scripts
```

* GIAnT config
```bash
export InSarFlow_HOME=/home/USERNAME/InSarFlow
export PYTHONPATH=$GIANT:$PYAPS:$VARRES:$InSarFlow_HOME/scripts
```
Note: Users need to open an account (free) on ASF to download SAR data.
Also, follow instruction [here](https://github.com/isce-framework/isce2) for automatic DEM download from https://urs.earthdata.nasa.gov/

## Try your first InSarFlow
#### 1. Create a csv file from ASF
Sentinel-1 and ALOS data can be accessed from [ASF](https://vertex.daac.asf.alaska.edu/). 

* Search your region of interest (*Note: At this moment, InSarFlow only supports ALOS and Sentinel-1*)
* Select an image that covers your area.
* Click on baseline, a PS Baseline Chart will open, showing information of all images for other days.
* Click on Export to CSV to download
* If your area doesn't fit into one image, you have to process for multiple paths/frames. 


#### 2. Processing interferograms
```bash
source ~/.ISCE_CONFIG   # Activate ISCE environment
cd path_to_your_project
python insar_XXXX.py
```

#### 3. Time-series analysis
```bash
source ~/.GIAnT
```

## Credits

## License
See the LICENSE file.


## Acknowledgments
Big thanks to the following people for contributing to this project in myriad ways:

* Luyen Bui
* Hai Pham 

## Author
* Phong Le: <mailto:levuvietphong@gmail.com>