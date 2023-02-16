# Knockai

Knock sensors are simple microphones. They are used by ECUs in a limited fashion to 
detect pre-detonation at a windowed frequency band that is typical to the pining sound produced
when gasoline pre-detonates.

By recording these sounds and analyzing them with modern datascience tools, we can detect pre-detonation and use it to enhance
an air-fuel / ignition map to run leaner and more efficiently while creating safe power.

The capabilities of python and the ML libraries available make this far superior to hardware and firmware
based approaches. However, the drawback being that it is not real-time and so won't save your engine.

## Hardware
- You will need a connection to the knock sensor on your engine with a device that you can record with the best quality possible.
- You will need a tunable ECU. If you don't have this, there is no point in using this software.
- You will need a way to log your ECU parameters.

## Other Requirements
- You will need a basic understanding of how your engine responds to tuning parameters
- You will need a basic understanding of how to use datascience tools like jupyter notebook
