UrJTAG is an open-source JTAG boundary scan software developed more than 10 year. It support many FPGA cables for flash programming. But there is limited support for hardware testing like verifying connectivity between ICs. The toggling pins using UrJTAG shell was tedius. 

As python integrated into UrJTAG, its easy to integrate a pin-toggling test by running walking 1's or 0's if you have BSDL files configured.

Make sure that you have compiled BSDL files to UrJTAG and kept in the same directory as mentioned in script
JTAG chain and cable can be tested in the UrJTAG shell before running python script.
How to install and all dependencies successfully also recaptured for your quick reference.

The script runs walkin 1's and 0's through the selected IC through EXTEST and observes the corresponding changes in the  SAMPLE command.
part numbers in the chain used for sample and extest is defined through the command line.

The below command  samples part 0 in the chain and drive part 1 in the chain for the resutls 

"sudo python walkin__sample_use_partid_cli_time.py --extest 1 --extestalias extest_device --sample 0 --samplealias sample_device --debug 0"


Refer http://urjtag.org for more details on UrJTAG.

**Warning: JTAG toggling can make permanently damage HW. This software is for hardware or embedded developers to test prototypes.**
