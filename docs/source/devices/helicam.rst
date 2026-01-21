HeliCam Camera
==============

Overview
~~~~~~~~

A production-ready labscript device driver for the **Heliotis HeliCam C3** 3D imaging camera. 
The driver provides full integration with the labscript suite experimental control framework using 
**direct libHeLIC control** rather than external frameworks like NI-IMAQdx.

Features:

- Hardware trigger synchronization with nanosecond precision
- Multiple imaging modes (RAW_IQ, AMPLITUDE, INTENSITY, 3D, etc.)
- Flexible attribute-based camera configuration
- Real-time image display and continuous preview
- Live frame rate monitoring (exponential moving average)
- Mock mode for testing without hardware
- Smart attribute caching to minimize camera reprogramming
- Thread-safe buffered acquisition with timeout protection
- Comprehensive HDF5 image storage with metadata

Installation
~~~~~~~~~~~~

Ensure the libHeLIC library (Heliotis HeliCam Python wrapper) is installed and available in the Python path:

.. code-block:: bash

   # Verify libHeLIC installation:
   python -c "import libhelic; print(libhelic.__file__)"

Install labscript_devices with HeliCam support:

.. code-block:: bash

   cd labscript_suite/labscript-devices
   pip install -e .

Usage
~~~~~

Connection Table Setup
``````````````````````

.. code-block:: python

   from labscript import *
   from labscript_devices.HeliCam import HeliCam
   
   # Create camera device (requires parent device with digital trigger output)
   camera = HeliCam(
       name='helicam',
       parent_device=your_daq_device,       # Must have digital output
       connection='PFI0',                   # Trigger output pin
       serial_number=0x12345678,            # Your camera's serial number
       trigger_duration=10e-6,              # 10 microsecond trigger pulse
       orientation='main_chamber',          # For image storage location
       camera_attributes={                  # libHeLIC settings
           'SensTqp': 540,                  # Integration time
           'SensNFrames': 100,              # Number of frames
           'CamMode': 4,                    # SIMPLE_MAX mode
           'TrigExtSrcSel': 0,              # Trigger source selection
       }
   )


Acquisition Modes
`````````````````

The HeliCam supports three operational modes:

**1. Snapshot Mode (Manual Mode)**

Acquire single frames interactively in BLACS:

- Click the **"Snap"** button to acquire a single frame
- Image displays in real-time in the PyQtGraph viewer
- Use the attributes dialog to adjust settings between snaps
- Useful for focusing and alignment

**2. Continuous Streaming Mode**

Stream frames continuously with adjustable frame rate:

- Click **"Continuous"** to start streaming
- Use the frame rate spinner (0 = unlimited)
- Click "Reset Rate" to remove frame rate limiting
- Click **"Stop"** to end streaming
- Useful for live preview during setup
- Frame rate determined by: exposure time + processing time + ZMQ transmission

**3. Timed Exposures in Experiment Shots**

Acquire images at precise times during automated experiment runs:

.. code-block:: python

   start()
   
   # Single exposure
   camera.expose(0.5, 'absorption_image', trigger_duration=10e-6)
   
   # Multiple frames from same state
   for i in range(5):
       camera.expose(0.5 + i*0.1, 'kinetics', 
                     frametype=f'frame_{i}', trigger_duration=10e-6)
   
   # Different image types (atoms vs. background)
   camera.expose(0.0, 'atoms', frametype='atoms', trigger_duration=10e-6)
   camera.expose(0.2, 'atoms', frametype='background', trigger_duration=10e-6)
   
   stop(5.0)


Camera Attributes
`````````````````

Common Configuration Attributes:

.. list-table::
   :header-rows: 1
   :widths: 20 15 50

   * - Attribute
     - Type
     - Description
   * - SensTqp
     - int (0-~3000)
     - Sensor integration time
   * - SensNFrames
     - int (1-65535)
     - Number of frames per trigger
   * - SensNavM2
     - int (0-1000)
     - Averaging/navigation factor
   * - CamMode
     - int (0-7)
     - Acquisition mode (see below)
   * - BSEnable
     - bool (0/1)
     - Background subtraction enable
   * - DdsGain
     - int (0-3)
     - DDS gain setting
   * - TrigFreeExtN
     - bool (0/1)
     - 0=free run, 1=external trigger
   * - TrigExtSrcSel
     - int
     - External trigger source selection
   * - ExSimpMaxHwin
     - int
     - Extended simple max window size
   * - Comp11to8
     - bool (0/1)
     - 11→8 bit compression

Imaging Modes (CamMode):

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - Value
     - Mode
     - Description
   * - 0
     - RAW_IQ
     - Complex raw data (In-phase/Quadrature channels)
   * - 1
     - AMPLITUDE
     - Amplitude measurements
   * - 2
     - SMOOTH_AMPLITUDE
     - Smoothed/filtered amplitude
   * - 3
     - INTENSITY
     - Power/intensity measurement
   * - 4
     - SIMPLE_MAX
     - Simple maximum (fastest, peak detection)
   * - 5
     - EXTENDED_SIMPLE_MAX
     - Extended peak detection with filtering
   * - 7
     - MIN_ENERGY
     - Minimum energy mode


Image Storage in HDF5
`````````````````````

Images are automatically saved in a hierarchical HDF5 structure:

.. code-block:: text

   /images/{orientation}/
   └── {exposure_name}/
       └── {frametype}  ← actual image data

Access in analysis code:

.. code-block:: python

   import h5py
   
   # In lyse analysis function:
   with h5py.File(filepath) as f:
       images = f['images/helicam/absorption_image']
       probe_image = images['probe'][:]        # numpy array
       atoms_image = images['atoms'][:]
       background = images['background'][:]


Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

For live preview (fast but noisier):

.. code-block:: python

   camera_attributes = {
       'SensTqp': 100,           # Short integration time
       'SensNavM2': 2,           # Minimal averaging
       'CamMode': 4,             # SIMPLE_MAX (fastest)
       'SensNFrames': 1,         # Single frame
   }

For clean science data (slower but cleaner):

.. code-block:: python

   camera_attributes = {
       'SensTqp': 10000,         # Long integration time
       'SensNavM2': 100,         # Heavy averaging
       'CamMode': 3,             # INTENSITY (cleaner)
       'SensNFrames': 150,       # More frames for averaging
   }


Troubleshooting
~~~~~~~~~~~~~~~

**Camera Not Found**

- Verify serial number matches device: run ``libHeLICTester.py`` test9
- Ensure camera is powered and USB cable connected
- Confirm libHeLIC library is installed: ``python -c "import libhelic"``

**Missed Triggers / Acquisition Timeouts**

- Verify trigger connection to camera trigger input
- Check trigger timing relative to integration time
- Increase ``stop_acquisition_timeout`` parameter if needed
- Reduce ``SensNFrames`` or increase ``SensTqp`` to speed acquisition

**No Images Saved to HDF5**

- Check ``failed_shot`` attribute in HDF5 output
- Verify trigger is actually reaching the camera using BLACS snap mode
- Ensure ``exception_on_failed_shot`` setting allows partial data

**Low Frame Rate in Continuous Mode**

- Reduce ``SensTqp`` (integration time)
- Reduce number of frames per trigger
- Disable other GUI elements consuming CPU
- Check system load with task manager

**Image Quality Issues**

- Adjust ``SensTqp`` to balance signal level and noise
- Enable/increase ``SensNavM2`` for averaging and noise reduction
- Try different ``CamMode`` for your specific application
- Verify optical focus and alignment

**Black Screen in Display**

- Check grayscale colormap initialization
- Verify images are being acquired (ZMQ frame rate display)
- Try restarting BLACS tab


Detailed Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   labscript_devices.HeliCam.labscript_devices
   labscript_devices.HeliCam.blacs_tabs
   labscript_devices.HeliCam.blacs_workers

.. automodule:: labscript_devices.HeliCam
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:

.. automodule:: labscript_devices.HeliCam.labscript_devices
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:

.. automodule:: labscript_devices.HeliCam.blacs_tabs
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:

.. automodule:: labscript_devices.HeliCam.blacs_workers
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
