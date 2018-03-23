# cryostatcontrol
CryostatControl is a control library for controlling and cycling a helium-3 sorption refrigerator at low temperature.

Project contains sub-modules:
`croystatcontrol.communicator` a general purpose method for letting multiple scripts address in-use locked hardware
`cryostatcontrol.hardware` a low-level pythonesque hardware library
`cryostatcontrol.controller` an abstracted control method using `hardware` and `communicator`
`cryostatcontrol.legacy` an old structure for controlling a cryostat
