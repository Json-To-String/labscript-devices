Heliotis HeliCam Camera
=======================

Overview
~~~~~~~~

Labscript device driver for the **Heliotis HeliCam C3** lock-in camera. 
Provides integration with the labscript suite framework using the HeliSDK
and associated LibHeLIC.

Features:

- TODO

Installation
~~~~~~~~~~~~

Ensure the libHeLIC library (Heliotis HeliCam Python wrapper) is installed.
The driver will attempt to import from the system's program files, which should
work with the default Heli-SDK install.

.. code-block:: python

  prgPath = os.environ["PROGRAMFILES"]

  sys.path.insert(0, prgPath + r"\Heliotis\heliCam\Python\wrapper")
  from libHeLIC import LibHeLIC  # noqa: E402

Usage
~~~~~

Example Connection Table
````````````````````````

.. code-block:: python

  from labscript import *
  from labscript_devices.HeliCam.labscript_devices import HeliCam
  from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
  from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice


  dummy_clock = DummyPseudoclock(name="dummy_clock", BLACS_connection="dummy")
  dummy_daq = DummyIntermediateDevice(
      name="dummy_device", BLACS_connection="dummy2", parent_device=dummy_clock.clockline
  )

  camera = HeliCam(
      name="helicam",
      parent_device=dummy_daq,
      connection="c3cam_s170",
      serial_number="008650",
      camera_attributes={
          "SensTqp": 4095,
          "SensNFrames": 16,
          "SensNavM2": 255,
          "CamMode": 0,
          "DdsGain": 2,
          "BSEnable": 0,
          "TrigFreeExtN": 1,
          "TrigExtSrcSel": 0,
          "AcqStop": 0,
          "EnSynFOut": 1,
      },
      # manual_mode_camera_attributes={
      #     'SensTqp' : 4095,           # Shorter integration for faster acquisition
      #     'SensNavM2' : 255,           # Minimal averaging for speed
      #     'TrigFreeExtN' : 1,        # Enable free-run mode (software trigger) for continuous
      # }
  )
  if __name__ == "__main__":
      start()

      stop(1)



Acquisition Modes (TODO)
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
     - int (1-4095)
     - Sensor integration time
   * - SensNFrames
     - int (1-512)
     - Number of frames per trigger
   * - SensNavM2
     - int (0-255)
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
     - 0=external trigger, 1=free run / internal
   * - TrigExtSrcSel
     - int
     - External trigger source selection

Supported Imaging Modes (CamMode):

.. list-table::
   :header-rows: 1
   :widths: 10 20 50

   * - Value
     - Mode
     - Description
   * - 0
     - RAW_IQ
     - Complex raw data (In-phase/Quadrature channels)
   * - 3
     - INTENSITY
     - Power/intensity measurement


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


Troubleshooting
~~~~~~~~~~~~~~~

**Camera Not Found**

- Verify serial number matches device: run ``libHeLICTester.py`` test9
- Ensure camera is powered and USB cable connected
- Confirm libHeLIC library is installed: ``python -c "import libhelic"``

**Missed Triggers / Acquisition Timeouts**

- Verify trigger connection to camera trigger input
- Check trigger timing relative to integration time
.. - Increase ``stop_acquisition_timeout`` parameter if needed
- Reduce ``SensNFrames`` or decrease ``SensNavM2`` to speed acquisition
- TODO: Framerate
  
**No Images Saved to HDF5**

- Check ``failed_shot`` attribute in HDF5 output
- Verify trigger is actually reaching the camera using BLACS snap mode
- Ensure ``exception_on_failed_shot`` setting allows partial data

**Black Screen in Display**

- TODO
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
