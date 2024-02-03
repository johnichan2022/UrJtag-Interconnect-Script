UrJTAG is an open-source JTAG boundary scan software developed more than 10 year. It support many FPGA cables for flash programming. But there is limited support for hardware testing like verifying connectivity between ICs. The toggling pins using UrJTAG shell was tedius. 

As python integrated into UrJTAG, its easy to integrate a pin-toggling test by running walking 1's or 0's if you have BSDL files configured.

Make sure that you have compiled BSDL files to UrJTAG and kept in the same directory as mentioned in script
JTAG chain and cable can be tested in the UrJTAG shell before running python script.

Warning: JTAG toggling can make permanently damage HW. This software is for hardware or embedded developers to test prototypes.

