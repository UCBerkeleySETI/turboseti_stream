r""" Code base for interfacing Gnu Radio functions with turbo_seti """

import os
import time
import logging
import math
import numpy as np
from pkg_resources import resource_filename

from h5py import __version__ as H5PY_VERSION
import setigen as stg
from blimpy import __version__ as BLIMPY_VERSION
from turbo_seti.find_doppler.kernels import Kernels
import turbo_seti.find_doppler.find_doppler as fd
from turbo_seti.find_doppler.file_writers import FileWriter, LogWriter
from turbo_seti.find_doppler.turbo_seti_version import TURBO_SETI_VERSION
from .version import TURBOSETI_STREAM_VERSION
VERSION_ANNOUNCEMENTS = 'turboseti_stream version {}\nturbo_seti version {}\nblimpy version {}\nh5py version {}\n\n' \
                        .format(TURBOSETI_STREAM_VERSION, TURBO_SETI_VERSION, BLIMPY_VERSION, H5PY_VERSION)


LOGGER_NAME = 'find_doppler'
logger = logging.getLogger(LOGGER_NAME)


class Map(dict):
    r"""
    A derivative of the Python dict class
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class DataLoader():
    r""" Load the data matrix (spectra), either by:
        1. A Gnu Radio function delivering telescope data.
        2. Synthetic data created by spectra_gen which uses setigen and configuration definitions.

        The later is used for unit/regression testing - see test_synth_data.py.
    """


    def __init__(self, data_obj, drift_indices):
        self.drift_indices = drift_indices
        self.data_obj = data_obj
        self.spectra = [0, 0]
        logger.debug("turboseti_stream DataLoader __init__: data_obj: {}".format(self.data_obj))


    def load(self, spectra):
        r""" Load telescope data from a Gnu Radio function """
        self.spectra = spectra
        logger.debug("turboseti_stream DataLoader load: spectra shape: {}".format(self.spectra.shape))


    def load_file(self, spectra_file_path):
        r""" Load synthetic data created by spectra_gen which uses setigen """
        frame = stg.Frame(spectra_file_path)
        self.spectra = frame.data
        logger.debug("turboseti_stream DataLoader load_file: spectra shape: {}".format(self.spectra.shape))


    def get(self):
        r""" called by turbo_seti find_doppler.py load_the_data() """
        return (self.data_obj, self.spectra, self.drift_indices)


class DopplerFinder():
    r""" Emulates the data portion of turbo_seti find_doppler find_doppler.py FindDoppler class """


    def __init__(self, filename, source_name, src_raj, src_dej,
                 tstart,
                 tsamp,
                 f_start,
                 f_stop,
                 n_fine_chans,
                 n_ints_in_file,
                 log_level_int=logging.INFO,
                 coarse_chan_num=0,
                 n_coarse_chan=1,
                 min_drift=0.00001,
                 max_drift=4.0,
                 snr=25.0,
                 out_dir='./',
                 flagging=False,
                 obs_info=None,
                 append_output=False,
                 blank_dc=True,
                 kernels=None,
                 gpu_backend=False,
                 precision=1,
                 gpu_id=0):
        r"""
        DopplerFinder class instantiation function.

        Parameters
        ----------
        tstart : float
            Observation start time in MJD.  
            Required.
        tsamp : float
            Time interval in seconds between integrations.  
            Required.
        f_start : float
            First frequency for the data matrix, corresponds to column 0.
            Required.
        f_stop : float
            Last frequency for the data matrix, corresponds to column -1.
            Required.
        n_fine_chans : int
            Number of fine channels in the data matrix (column count).  
            Required.
        n_ints_in_file : int
            Number of time integrations in the data matrix (row count).  
            Required.
        log_level_int : int
            Logging level used by turbo_seti:
                logging.DEBUG (10)
                logging.INFO (20)
                logging.WARNINS (30)
                logging.ERROR (40)
                logging.CRITICAL (50)
            Default: logging.INFO.
        coarse_chan_num : list
            List of specific coarse channels to analyze.
            By default, all coarse channels will be searched.
            Use this to search only specified channels. E.g. coarse_chan_num=[7,12] 
            will cause a search of only coarse channels 7 and 12.
            Default: None.
        n_coarse_chan : int
            Number of coarse channels.
            Default: 1 (okay for Gnu Radio; not recommended, in general).
        min_drift : float
            Minimum drift rate (lower limit) of a signal to qualify as a hit.
            Default: 0.00001.
        max_drift : float
            Maximum drift rate (upper limit) of a signal to qualify as a hit.
            Default: 4.
        snr : float
            Minimum SNR value (lower limit) of a signal to qualify as a hit.
            Default: 25.
        out_dir : str,
            Output directory for turbo_seti to store the resulting .dat and .log files.
            Default: current directory.
        flagging : bool
            Rarely if ever used. I hope that a SETI-BL or ATA scientist can define this.
            Default: False.
        obs_info : dict
            Rarely if ever used. Information elements about pulsars, RFI, and SEFD.
            Default: {'pulsar': 0, 'pulsar_found': 0, 'pulsar_dm': 0.0, 'pulsar_snr': 0.0,
                        'pulsar_stats': self.kernels.np.zeros(6), 'RFI_level': 0.0, 
                        'Mean_SEFD': 0.0, 'psrflux_Sens': 0.0,
                        'SEFDs_val': [0.0], 'SEFDs_freq': [0.0], 'SEFDs_freq_up': [0.0]}
        blank_dc : bool
            Smoothe out spikes in the middle of a coarse channel? (True/False).
        gpu_backend : bool
            Use Nvidia GPU? (True/False).  Default: False.
        precision : int
            GPU precision: 1=single, 2=double.  Single precision seems to be the best choice.
            Default: 1
        gpu_id : int
            GPU device ID.  Default: 0.

        Returns
        -------
        DopplerFinder object.

        """

        logger.setLevel(log_level_int)
        self.filename = filename
        self.out_dir = out_dir

        if not kernels:
            self.kernels = Kernels(gpu_backend, precision, gpu_id)
        else:
            self.kernels = kernels

        if obs_info is None:
            obs_info = {'pulsar': 0, 'pulsar_found': 0, 'pulsar_dm': 0.0, 'pulsar_snr': 0.0,
                        'pulsar_stats': self.kernels.np.zeros(6), 'RFI_level': 0.0, 'Mean_SEFD': 0.0, 'psrflux_Sens': 0.0,
                        'SEFDs_val': [0.0], 'SEFDs_freq': [0.0], 'SEFDs_freq_up': [0.0]}

        fftlen = n_fine_chans
        shoulder_size = 0
        tsteps_valid = n_ints_in_file
        tsteps = int(math.pow(2, math.ceil(np.log2(math.floor(n_ints_in_file)))))

        # Data Object Header - not to be confused with a Filterbank/HDF5 file header!
        # This will be used subsequently as an element of self.data_dict.
        # In turbo_seti, this is created in find_doppler data_handler.py
        self.header = Map({
            "coarse_chan": 0, # Coarse channel number, NOT the same as n_coarse_chan == the amount of coarse channels?
            "obs_length": n_ints_in_file * tsamp,
            "DELTAF": (f_stop - f_start) / n_fine_chans,
            "NAXIS1": fftlen,
            "FCNTR": (f_stop + f_start) / 2, # 1/2 way pt between the lowest and highest fine channel frequency
            "baryv": 0, # Never used anywhere
            "SOURCE": source_name, # ATA Track Scan takes source name/id OR ra/dec OR az/el
            "MJD": tstart, # Observation start time, from ATA block
            "RA": src_raj,
            "DEC": src_dej,
            "DELTAT": tsamp, # Time step in seconds
            "max_drift_rate": max_drift,
        })

        # In turbo_seti, this object is nearly the same as the FindDoppler object.
        self.find_doppler_instance = Map({
            "data_handle": Map({
                "filename": filename,
                "header": self.header
            }),
            "log_level_int": log_level_int,
            "min_drift": min_drift,
            "max_drift": max_drift,
            "out_dir": out_dir,
            "snr": snr,
            "status": True,
            "flagging": flagging,
            "obs_info": obs_info,
            "append_output": append_output,
            "flag_blank_dc": blank_dc,
            "n_coarse_chan": n_coarse_chan,
            "kernels": self.kernels,
        })

        # In turbo_seti, this object is nearly the same as the DATAH5 object in data_handler.py.
        self.data_dict = Map({
            "f_start": f_start,
            "f_stop": f_stop,
            "tsteps_valid": tsteps_valid,
            "tsteps": tsteps,
            "tdwidth": int(fftlen + shoulder_size * tsteps),
            "fftlen": n_fine_chans // n_coarse_chan,
            "shoulder_size": shoulder_size,
            "drift_rate_resolution": (1e6 * np.abs(self.header['DELTAF'])) / self.header['obs_length'],
            "coarse_chan": coarse_chan_num,
            "header": self.header
        })

        # Create Custom Data Loader to be used in find_doppler.py load_the_data().
        # Start with the drift_indixes object.
        dia_num = int(np.log2(self.data_dict.tsteps))
        file_path = resource_filename('turbo_seti', f'drift_indexes/drift_indexes_array_{dia_num}.txt')
        logger.debug("turboseti_stream drift_indexes tsteps={}, dia_num={}"
                     .format(self.data_dict.tsteps, dia_num))
        logger.debug("turboseti_stream drift_indexes file_path={}".format(file_path))

        assert os.path.isfile(file_path) # File exists?

        di_array = np.array(np.genfromtxt(file_path, delimiter=' ', dtype=int))
        logger.debug("turboseti_stream drift_indexes di_array.shape: {}".format(di_array.shape))

        ts2 = int(self.data_dict.tsteps / 2)
        logger.debug("turboseti_stream self.data_dict.tsteps_valid - 1 - ts2: " 
                     + str(self.data_dict.tsteps_valid - 1 - ts2))
        drift_indexes = di_array[(self.data_dict.tsteps_valid - 1 - ts2), 0:self.data_dict.tsteps_valid]

        # Create the DataLoader object.
        self.dataloader = DataLoader(self.data_dict, drift_indexes)


    def _find_ET_common(self):
        wfilename = self.filename.split('/')[-1].replace('.h5', '').replace('.fil', '')
        path_log = '{}/{}.log'.format(self.out_dir.rstrip('/'), wfilename)
        path_dat = '{}/{}.dat'.format(self.out_dir.rstrip('/'), wfilename)
        if os.path.exists(path_log):
            os.remove(path_log)
        if os.path.exists(path_dat):
            os.remove(path_dat)
        with open(path_log, "w") as fav:
            fav.write(VERSION_ANNOUNCEMENTS)
            fav.write("turboseti_stream find_doppler_instance: {}\n\n".format(self.find_doppler_instance))
            fav.write("turboseti_stream data_dict: {}\n\n".format(self.data_dict))
        logwriter = LogWriter(path_log)
        filewriter = FileWriter(path_dat, self.header)
        
        t1 = time.time()
        fd.search_coarse_channel(self.data_dict,
                                 self.find_doppler_instance,
                                 dataloader=self.dataloader,
                                 logwriter=logwriter,
                                 filewriter=filewriter)
        msg = "\nturboseti_stream search_coarse_channel() completed in {:0.1f}s\n" \
              .format(time.time() - t1)
        with open(path_log, "a") as fav:
            fav.write(msg)
        logger.debug(msg)


    def find_ET(self, spectra):
        r""" find ET using a spectra matrix supplied by Gnu Radio """
        self.dataloader.load(spectra)
        self._find_ET_common()


    def find_ET_from_file(self, spectra_file_path):
        r""" find ET using a spectra matrix supplied by spectra_gen (synthetic) """
        self.dataloader.load_file(spectra_file_path)
        self._find_ET_common()

