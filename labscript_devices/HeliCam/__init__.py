#####################################################################
#                                                                   #
# /labscript_devices/HeliCam/__init__.py                           #
#                                                                   #
# Copyright 2019, Monash University and contributors                #
#                                                                   #
# This file is part of labscript_devices, in the labscript suite    #
# (see http://labscriptsuite.org), and is licensed under the        #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################

"""
Labscript device driver for Heliotis HeliCam C3 camera.

This package provides full integration of the Heliotis HeliCam C3 3D imaging
camera with the labscript suite. The HeliCam is a high-speed camera capable of
3D surface measurement and various intensity/amplitude imaging modes.
The driver uses the libHeLIC Python library for direct camera control, avoiding
dependencies on external frameworks like NI-IMAQdx.
Modules:
    labscript_devices: Device driver for use in labscript connection tables
    blacs_workers: BLACS worker for camera control and image acquisition
    blacs_tabs: BLACS GUI tab for user interaction
    register_classes: Registration of device and GUI classes with labscript

The device supports:
    - Hardware trigger synchronization with experiments
    - Multiple imaging modes (Raw IQ, Amplitude, Intensity, 3D)
    - Live preview during experiment setup
    - Automatic image storage to HDF5 files
    - Camera attribute configuration and inspection

Example connection table usage:

    from labscript import *
    from labscript_devices.HeliCam import HeliCam
    
    # Assuming a parent device (e.g., NI DAQ) with digital output:
    camera = HeliCam(
        name='camera',
        parent_device=DigitalOut_Device,
        connection='PFI0',
        serial_number=0x12345678,  # Camera serial number
        trigger_duration=10e-6,     # 10 microsecond trigger pulse
        camera_attributes={
            'SensTqp': 540,              # Integration time
            'SensNFrames': 100,          # Number of frames
            'CamMode': 4,                # SIMPLE_MAX mode
            'BSEnable': 1,               # Enable background subtraction
            'TrigExtSrcSel': 0,          # External trigger source
        }
    )
    
    # Request images in the experiment:
    camera.expose(0.0, 'image1', trigger_duration=10e-6)
    camera.expose(1.0, 'image2', trigger_duration=10e-6)

Attributes Documentation:
    The libHeLIC library provides many configurable attributes controlling
    various aspects of image acquisition. Common attributes include:
    
    - SensTqp: Sensor time-of-flight parameter (integration time)
    - SensNavM2: Navigation mode
    - SensNFrames: Number of frames to acquire
    - CamMode: Camera operating mode
        - 0: RAW_IQ - Raw in-phase/quadrature data
        - 1: AMPLITUDE - Amplitude measurements
        - 2: SMOOTH_AMPLITUDE - Smoothed amplitude
        - 3: INTENSITY - Intensity imaging
        - 4: SIMPLE_MAX - Simple max mode
        - 5: EXTENDED_SIMPLE_MAX - Extended max with filtering
        - 7: MIN_ENERGY - Minimum energy mode
    - BSEnable: Background subtraction enable (0/1)
    - DdsGain: DDS (Direct Digital Synthesizer) gain
    - TrigFreeExtN: Free/external trigger enable
    - TrigExtSrcSel: External trigger source selection
    - ExSimpMaxHwin: Extended simple max filter window

Hardware Trigger Requirements:
    The camera expects a digital trigger pulse on its trigger input. The
    trigger duration and edge type should be configured to match the camera's
    trigger requirements (typically a falling edge, 100ns-1000ns pulse).

Dependencies:
    - libHeLIC: Heliotis HeliCam Python library (REQUIRED)
    - labscript: Experiment control framework
    - h5py, numpy, zmq, pyqtgraph, Qt5: Standard dependencies
    
    NOTE: This implementation does NOT require NI-IMAQdx or pynivision.
    It communicates directly with the camera via libHeLIC.

See Also:
    - Heliotis documentation for libHeLIC API details
    - labscript documentation for connection table configuration
"""