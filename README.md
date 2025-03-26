# open-souce-SWLI
An open source scanning white light interferometer (SWLI) project.
# this is WORK IN PROGRESS!
### To contribute get in touch with #wokileo on Discord.

## Introduction
What is a scanning white light interferometer?  
...


## Project Goals
- [ ] Create the optics setup 
- [ ] Create the mechanical setup for Z-axis scanning
- [ ] Create the mechanical setup for XY-axis scanning
- [ ] affordable
- [ ] easy to use
- [ ] easy to build
- [ ] easy to modify
- [ ] easy to calibrate
- [ ] high resolution
- [ ] Create a simple and easy to understand processing pipeline for the data


## Project Structure
- [ ] Optics
- [ ] Mechanics
- [ ] Electronics
- [ ] Software
- [ ] Documentation
- [ ] Testing

## Optics
- [ ] Choose Interferometer type: `Michelson`,`Linnik` or `other?`
  - Temperature stability
  - cost
  - ease of alignment
  - optical path length
  - magnification
  - field of view
  - resolution
- [ ] White light source
- [ ] Beam splitter
- [ ] Mirrors
- [ ] Objective lens
- [ ] Camera
- [ ] Calibration

References:
- https://youtu.be/YxO5l2tML7o?si=CXOTyoQOTEporDHH

## Mechanics
- [ ] Z-axis
- [ ] XY-axis
- [ ] Frame
- [ ] Enclosure
- [ ] Calibration
- [ ] Assembly
- [ ] Tools

### What to keep in mind when designing the mechanics?
- Temperature stability of the system
  - avoid plastics where possible
  - use materials with low thermal expansion: `Carbon fiber`, `Steel`, `Robax glass`
- High resonant frequencies
  - high Stiffness
  - Low mass
- Vibration isolation
- Accessibility of the part
- Ease of assembly

## Z-Axis
- Drive mechanism
  - Stepper motor + Micrometer screw + Flexture based reducer
  - Piezo actuator
- Linear guide: `Flexture` 
- Positional resolution: ideally `1 nm`
- Positional accuracy: `???`
- Positional repeatability: `how good can we get this?`
- Positional range: `0,05 to 1mm`
- Velocity: `low`
- Acceleration: `negligible`
- Drive control: `open-loop`
- mechanism height: `<40mm`

## Electronics
- [ ] Camera interface: `USB?`
- [ ] Z-axis motor control: `via Arduino?`
- [ ] XY-axis motor control: `via Arduino?`
- [ ] Power supply

## Software
- [x] Programming language: `Python`
- [ ] create general structure
- [ ] measurement control
  - [ ] Data acquisition
  - [ ] Data storage
  - [ ] Drive control
- [ ] Data processing
  - [ ] Image acquisition from hard drive
  - [ ] Image filtering
  - [ ] Image processing to get height data
  - [ ] apply Calibration offsets
  - [ ] height data filtering
  - [ ] Optional: Image stitching
  - [ ] Data visualization
  - [ ] Optimize for performance and accuracy

References:
- https://github.com/Javassss/WLI_scanning
- https://github.com/asingleoat/oatSWLI
- Matlab code by cyrus can be found in the src folder

## Documentation
- [ ] Assembly instructions
- [ ] User manual
- [ ] Troubleshooting
- [ ] Bill of materials
- [ ] Tools
- [ ] Software installation
- [ ] Software usage
- [ ] Hardware installation
- [ ] Hardware usage
- [ ] Contributing
- [ ] Testing
- [ ] Calibration