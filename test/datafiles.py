import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CFG_FILE = os.path.join(HERE, "sample_spectra_gen.cfg")
TEMPDIR = tempfile.gettempdir() + "/turboseti_stream_"+ str(os.getpid()) + "/"
SYNTH_FILE = TEMPDIR + "turboseti_stream.fil"
MAX_DRIFT_RATE = 4.0
MIN_SNR = 25.0

if not os.path.isdir(TEMPDIR):
    os.makedirs(TEMPDIR)
