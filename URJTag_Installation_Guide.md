# Universal JTAG library installation
JTAG (IEEE 1149.1) is a serial interface for testing devices with integrated circuits. The problem that the JTAG interface was designed to solve is checking if connections between ICs are OK. Therefore you can set and check in- and outputs of ICs. In order to save pins and logic a very simple serial design was invented.

- One pin serial input
- One pin serial output
- One pin clock
- One pin control

The control pin (together with clock) allows to switch device states. A state machine inside each chip can be controlled, e.g. to reset the device. This control machine also allows to have two internal shift registers in each device (although we only have on in- and one output-pin). The registers are called instruction register (IR) and data register (DR). The current UrJTAG tool allows you to set the IR and set and get the DR. It doesn’t allow you to directly control the state machine (yet).

UrJTAG is a software package which enables working with JTAG-aware (IEEE 1149.1) hardware devices (parts) and boards through a JTAG adapter. This package has an open and modular architecture with the ability to write miscellaneous extensions (like board testers, flash memory programmers, and so on).

### Install Subversion
This command installs the Subversion version control system, which is required for fetching the URJTAG source code.
```bash
sudo apt install subversion
```

### Fetch URJTAG Source Code
Now, you can proceed to checkout the specific revision (2055) of the URJTAG source code from the Subversion repository. Use the following command:
```bash
sudo svn checkout https://svn.code.sf.net/p/urjtag/svn/trunk@2055 2055
```
After checking out the URJTAG source code at revision 2055, navigate to the "urjtag" directory using the following command:
```bash
cd 2055/urjtag/
```
### Update and Upgrade System Packages
Ensure your system packages are up-to-date by running the following commands:
```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

### Install Essential Tools
Install essential tools and dependencies for software development:
```bash
sudo apt-get install git git-core autoconf build-essential libtool
```

### Install Python Development Tools
Install Python development tools and dependencies:
```bash
sudo apt-get install libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev

sudo apt-get  install python3-dev python3-distutils python3-pip
```

### Install libftdi
Install libftdi and its development files:
```bash
sudo apt-get install libftdi-dev
```

### Install libusb-1.0
Install libusb-1.0 and its development files:
```bash
sudo apt-get install libusb-1.0-0-dev
```

### Install Autopoint, Flex, Bison, and Byacc
```bash
sudo apt-get install autopoint
sudo apt-get install flex
sudo apt-get install bison
sudo apt-get -y install byacc
```
### Install Glibc Source
```bash
sudo apt install glibc-source -y
```

### Install Readline Common
```bash
sudo apt-get -y install readline-common
```

### Install libftdi1
```bash
sudo apt-get install -y libftdi1
```

### Updating Ownership for URJTAG Source Code
The URJTAG folder is fetched using sudo, resulting in root ownership. To rectify this, use the following commands to change ownership and group ownership to the current user:
```bash
sudo chown -R $USER ./*
sudo chgrp -R $USER ./*
```

### Custom Configuration in autogen.sh
To customize the configuration in the ./autogen.sh file for your URJTAG source code, replace the following line:
```bash
./configure --enable-maintainer-mode --with-libusb --with-libftdi --with-ftd2xx "$@"
```

### Build and Install

```bash
sudo ./autogen.sh
```
Initiates the compilation process based on the configured settings.
```bash
sudo make
```
Installs the compiled binaries and associated files to the system.
```bash
sudo make install
```
Updates the dynamic linker runtime bindings. It's necessary after installing new libraries or shared objects.
```bash
sudo ldconfig
```

### Run 
Executes the jtag command with elevated privileges, typically used to interact with JTAG interfaces and devices.
```bash
sudo jtag
```