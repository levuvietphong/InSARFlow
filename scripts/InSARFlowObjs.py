
class ALOS_Options:
     """
     Options for ALOS Processing in ISCE
     .. version:: 0.1.0

     Notes
     -----
     This class is useful for creating options to control ISCE processing
     of ALOS data. 

     """
     def __init__(self,  Mode, DownloadImages=None, UnzipData=None, 
                         BaselineCheck=None, RemoveUnsedPairs=None, 
                         GenerateXML=None, RunIFGs=None, MPIMultipleNodes = None,
                         GenerateRoipac=None, CleanFiles=None,
                         TemporalBaselineThreshold=None, 
                         PerpendicularBaselineThreshold=None,
                         OpenMP_Num_Threads=None):
          
          # SET OPTIONS and PARAMETERS for ALOS PROCESSING
          # Select either 'insar' or 'stripmap' mode
          self.ProcessingMode = Mode

          # Downloading data
          self.DownloadImages = DownloadImages if DownloadImages is not None else 'true'
          
          # Unzipping data
          self.UnzipData = UnzipData if UnzipData is not None else 'true'
          
          # Baseline check for pairing
          self.BaselineCheck = BaselineCheck if BaselineCheck is not None else 'true'
          
          # Removing redundant files and folders
          self.RemoveUnsedPairs = RemoveUnsedPairs if RemoveUnsedPairs is not None else 'true'
          
          # Create XML files for isce processing
          self.GenerateXML = GenerateXML if GenerateXML is not None else 'true'
          
          # Running interferograms
          self.RunIFGs = RunIFGs if RunIFGs is not None else 'true'

          # Running ISCE processing in parallel using MPI
          self.MPIMultipleNodes = MPIMultipleNodes if MPIMultipleNodes is not None else 'false'

          # Preparing roipac format for GIAnT
          self.GenerateRoipac = GenerateRoipac if GenerateRoipac is not None else 'true'

          # Cleaning unused file for GIAnT
          self.CleanFiles = CleanFiles if CleanFiles is not None else 'true'

          # Temporal and Perpendicular Baselines
          self.TemporalBaselineThreshold = TemporalBaselineThreshold if TemporalBaselineThreshold is not None else 1000        # [day]
          self.PerpendicularBaselineThreshold  = PerpendicularBaselineThreshold if PerpendicularBaselineThreshold is not None else 700    # [m]

          # OpenMP Threads using for parallel
          self.OpenMP_Num_Threads = OpenMP_Num_Threads if OpenMP_Num_Threads is not None else 20


class SEN1A_Options:
     """
     Options for SENTINEL1A Processing in ISCE
     .. version:: 0.1.0

     Notes
     -----
     This class is designed for creating options to control ISCE processing
     of Sentinel-1A data. 

     """
     def __init__(self,  DownloadImages=None, GenerateXML=None, RunIFGs=None, 
                         MPIMultipleNodes = None, GenerateRoipac=None, 
                         CleanFiles=None, SelectRegion=None,                         
                         minLatitude=None, maxLatitude=None, minLongitude=None, maxLongitude=None,
                         TemporalBaselineThreshold=None, OpenMP_Num_Threads=None):

          # SET OPTIONS and PARAMETERS for SENTINEL-1A PROCESSING

          # Downloading data
          self.DownloadImages = DownloadImages if DownloadImages is not None else 'true'                    

          # Create XML files for isce processing
          self.GenerateXML = GenerateXML if GenerateXML is not None else 'true'

          # Select region of interest
          self.SelectRegion = SelectRegion if SelectRegion is not None else 'false'
          self.minLatitude = minLatitude if minLatitude is not None else None
          self.maxLatitude = maxLatitude if maxLatitude is not None else None
          self.minLongitude = minLongitude if minLongitude is not None else None
          self.maxLongitude = maxLongitude if maxLongitude is not None else None
                                        
          # Running interferograms
          self.RunIFGs = RunIFGs if RunIFGs is not None else 'true'

          # Running ISCE processing in parallel using MPI
          self.MPIMultipleNodes = MPIMultipleNodes if MPIMultipleNodes is not None else 'false'

          # Preparing roipac format for GIAnT
          self.GenerateRoipac = GenerateRoipac if GenerateRoipac is not None else 'true'

          # Cleaning unused file for GIAnT
          self.CleanFiles = CleanFiles if CleanFiles is not None else 'true'

          # Temporal and Perpendicular Baselines
          self.TemporalBaselineThreshold = TemporalBaselineThreshold if TemporalBaselineThreshold is not None else 30        # unit [day]

          # OpenMP Threads using for parallel
          self.OpenMP_Num_Threads = OpenMP_Num_Threads if OpenMP_Num_Threads is not None else 20


class ALOS_Lists:
     """
     List of files and folders for ALOS Processing in ISCE
     .. version:: 0.1.0
     """
     def __init__(self,  Project = None, Platform = None, LogFiles = None, 
                         dateID = None, LogScreen = None, ALOSScenes = None, 
                         DatePairList = None, ActiveList = None, CompleteList = None,
                         BoundBox = None, IfgList = None, SubData = None, 
                         ZipDirectory = None, RawDirectory = None,
                         ISCEDirectory = None, GIAnTDirectory = None,
                         MISCDirectory = None):

          # LIST OF FILES AND DIRECTORIES FOR ALOS PROCESSING
          # Project name
          self.Project = Project if Project is not None else 'PROJECT_ALOS'

          # Platform
          self.Platform = Platform if Platform is not None else 'ALOS'

          # Log files
          self.LogFiles = LogFiles if LogFiles is not None else 'log_ALOS.txt'

          # File contains date information of images
          self.dateID = dateID if dateID is not None else 'dateID.info'

          # File contains date information of images
          self.LogScreen = LogScreen if LogScreen is not None else 'screen.log'

          # File contains date information of images
          self.ALOSScenes = ALOSScenes if ALOSScenes is not None else 'ALOS_scenes.info'

          # File contains date information of images
          self.DatePairList = DatePairList if DatePairList is not None else 'list_date_pair.info'

          # Lists contains info of active/complete pairs
          self.ActiveList = ActiveList if ActiveList is not None else 'list_ifgs_active.info'
          self.CompleteList = CompleteList if CompleteList is not None else 'list_ifgs_complete.info'

          # File contains date information of images
          self.BoundBox = BoundBox if BoundBox is not None else 'boundbox.list'

          # File contains date information of images
          self.IfgList = IfgList if IfgList is not None else 'ifg.list'

          # File contains date information of images
          self.SubData = SubData if SubData is not None else 'subdata.csv'

          # Folder contains zipped images
          self.ZipDirectory = ZipDirectory if ZipDirectory is not None else 'ALOS_zip'

          # Folder contains raw images
          self.RawDirectory = RawDirectory if RawDirectory is not None else 'ALOS_raw'

          # Folder contains interferograms 
          self.ISCEDirectory = ISCEDirectory if ISCEDirectory is not None else 'INSAR'

          # Folder contains file for GIAnT processing
          self.GIAnTDirectory = GIAnTDirectory if GIAnTDirectory is not None else 'GIAnT'

          # Miscellaneous Folder
          self.MISCDirectory = MISCDirectory if MISCDirectory is not None else 'MISC'


class SEN1A_Lists:
     """
     List of files and folders for SENTINEL-1A Processing in ISCE
     .. version:: 0.1.0
     """
     def __init__(self,  Project = None, Platform = None, LogFiles = None, AuxLink = None, 
                         LogScreen = None, DatePairList = None, ActiveList = None, 
                         CompleteList = None,BoundBox = None, IfgList = None, SubData = None, 
                         SLCDirectory = None, AuxDirectory = None, PoeDirectory = None, 
                         ISCEDirectory = None, GIAnTDirectory = None,MISCDirectory = None):

          # LIST OF FILES AND DIRECTORIES FOR ALOS PROCESSING
          # Project name
          self.Project = Project if Project is not None else 'PROJECT_SEN1A'

          # Platform
          self.Platform = Platform if Platform is not None else 'SENTINEL-1A'

          # Log files
          self.LogFiles = LogFiles if LogFiles is not None else 'log_SEN1A.txt'
          
          # Auxiliary link
          self.AuxLink = AuxLink if AuxLink is not None else 'AuxLink not found'
          
          # File contains date information of images
          self.LogScreen = LogScreen if LogScreen is not None else 'screen.log'

          # File contains date information of images
          self.DatePairList = DatePairList if DatePairList is not None else 'list_date_pair.info'

          # Lists contains info of active/complete pairs
          self.ActiveList = ActiveList if ActiveList is not None else 'list_ifgs_active.info'
          self.CompleteList = CompleteList if CompleteList is not None else 'list_ifgs_complete.info'

          # File contains date information of images
          self.BoundBox = BoundBox if BoundBox is not None else 'boundbox.list'

          # File contains date information of images
          self.IfgList = IfgList if IfgList is not None else 'ifg.list'

          # File contains date information of images
          self.SubData = SubData if SubData is not None else 'subdata.csv'

          # Folder contains SLCs images
          self.SLCDirectory = SLCDirectory if SLCDirectory is not None else 'SLCs'

          # Folder contains AUX infor
          self.AuxDirectory = AuxDirectory if AuxDirectory is not None else 'AUXILIARY'
          
          # Folder contains POEORB files
          self.PoeDirectory = PoeDirectory if PoeDirectory is not None else 'POEORB'          

          # Folder contains interferograms 
          self.ISCEDirectory = ISCEDirectory if ISCEDirectory is not None else 'ISCE'

          # Folder contains file for GIAnT processing
          self.GIAnTDirectory = GIAnTDirectory if GIAnTDirectory is not None else 'GIAnT'

          # Miscellaneous Folder
          self.MISCDirectory = MISCDirectory if MISCDirectory is not None else 'MISC'
