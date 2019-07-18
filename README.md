<p align="left">
<img src="logo.png" alt="" width="600"/>
</p>

## Getting Started
As [Interferometric Synthetic Aperture Radar (InSAR)](https://en.wikipedia.org/wiki/Interferometric_synthetic-aperture_radar) data becomes increasingly popular, the ability to process these large datasets for time-series analysis is important.
InSARFlow utilizes [mpi4py](https://pypi.org/project/mpi4py/) for parallel processing of SAR interferograms and time-series analysis based on [ISCE](https://winsar.unavco.org/software/isce) and [GIAnT](http://earthdef.caltech.edu/projects/giant/wiki#) models.

InSARFlow has the following features:

- **Automatic downloading** SAR data from [Alaska Satellite Facility (ASF)](https://vertex.daac.asf.alaska.edu/).
- **Parallel processing** of interferograms. Because ISCE processing for each interferogram is independent, running ISCE for many pairs can be implemented very efficiently in parallel. Using [Message Passing Interface (MPI)](https://en.wikipedia.org/wiki/Message_Passing_Interface), InSARFlow supports large-scale processing on clusters and supercomputers.

## Prerequisite

The following packages are required for running InSARFlow:

* [ISCE 2.2.0](https://winsar.unavco.org/software/isce) (See [here](https://github.com/scottyhq/isce_notes/tree/master/Ubuntu) for installation instruction)
* [GIAnT](http://earthdef.caltech.edu/projects/giant/wiki#)
* [mpi4py](https://pypi.org/project/mpi4py/)
* [networkX](https://networkx.github.io/)
* [pandas](https://pandas.pydata.org/)


## Installation
Download and extract the code (name it InSARFlow) to your home folder. Add the following to your .bashrc file:
```bash
export PATH=$PATH:/home/USERNAME/InSARFlow/scripts
```

I setup ISCE and GIAnT in 2 separate environments.
For ISCE and GIAnT to recognize InSARFlow, add InSARFlow/scripts folder to the PYTHONPATH of each environment

* ISCE config
```bash
export InSARFlow_HOME=/home/USERNAME/InSARFlow
export PYTHONPATH=$ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component:$InSARFlow_HOME/scripts
```

* GIAnT config
```bash
export InSARFlow_HOME=/home/USERNAME/InSARFlow
export PYTHONPATH=$GIANT:$PYAPS:$VARRES:$InSARFlow_HOME/scripts
```

* For making Python scripts executable and runnable from anywhere, run the following:
```bash
chmod +x /home/USERNAME/InSARFlow/scripts/*.py
```

Note: User needs to open an account (free) on ASF to download SAR data.
Also, follow the instruction [here](https://github.com/isce-framework/isce2) for automatic DEM download from https://urs.earthdata.nasa.gov/


## Try your first InSARFlow
#### 1. Create a csv file from ASF
Sentinel-1 and ALOS data can be accessed from [ASF](https://vertex.daac.asf.alaska.edu/). 

* Search your region of interest (*Note: At this moment, InSARFlow only supports ALOS and Sentinel-1*)
* Select an image that covers your area.
* Click on baseline, a PS Baseline Chart will open, showing information of all images for other days.
* Click on Export to CSV to download
* If your area doesn't fit into one image, you have to process for multiple paths/frames. 


#### 2. Processing interferograms
To run ISCE, you must set the parameters: *RunScript = True* in the [ISCE] group
```bash
source ~/.ISCE_CONFIG   # Activate ISCE env
cd /home/USERNAME/InSARFlow/examples/MekongDelta
InSARFlow.py -c Mekong_SEN1A.cfg
```

#### 3. Time-series analysis
To run ISCE, you must set the options appropriately in the [GIANT] group.
Note that GIAnT must be run after ISCE is done.
```bash
source ~/.GIAnT         # Activate GIANT env
cd /home/USERNAME/InSARFlow/examples/MekongDelta
InSARFlow.py -c Mekong_SEN1A.cfg
```

*Note: For large-scale processing, the storage may reach 100s GB or > 1TB, so move the example folder to disks that have enough free space. The example folder is not neccessary to be in the InSARFlow directory*

## License
See LICENSE file for more information.


## Acknowledgments
Big thanks to the following people for contributing to this project in myriad ways:

* Luyen Bui
* Hai Pham 

## Author
* Phong Le: <levuvietphong@gmail.com>