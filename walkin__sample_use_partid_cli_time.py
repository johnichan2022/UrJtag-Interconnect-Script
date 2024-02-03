"""
Hardware Connection Test Script

Description:
This Python script is designed to test hardware connections using the urJTAG library. The script checks the connectivity and functionality of JTAG (Joint Test Action Group) interfaces with the connected hardware.

Dependencies:
- urJTAG: Ensure that urJTAG is installed on the system. You can install it using the package manager or by following the instructions on the urJTAG website (http://urjtag.org/book/_compilation_and_installation.html).

Usage:
1. Connect the hardware to the JTAG interface.
2. Run this script to perform a hardware connection test.
3. The script will communicate with the connected hardware using urJTAG and provide feedback on the status of the connections.

Note:
- Make sure to configure the JTAG chain properly in the urJTAG configuration file.
- This script assumes that urJTAG is available in the system's PATH.

Authors:
- Johnson
- Jobin

Version: v1.1

Date: 29 Dec 2023 

"""


# ==================================================================#
#                             LIBRARIES                             #
# ==================================================================#

import sys
import argparse
import urjtag
import keyboard
import time

# ==================================================================#
#                  LOG - HELP - TIME - PATH CONFIGURATIONS          #
# ==================================================================#

# This value can be modified by the cli argument. [--debug 0/1]
DEBUG = True

sys.path.append( "." )
urjtag.loglevel(urjtag.URJ_LOG_LEVEL_WARNING)
# Record the start time
start_time = time.time()

# seperation line pattern
LINE = "=" * 80

# 0 - extest
# 1 - sample
ALIAS_LIST = [None,None]

# to store the current walk-in state for controlling the summary result.
walkin_state = -1
# to store summary data for each walk
summary_list = []

# ==================================================================#
#                         CONFIGURATIONS                            #
# ==================================================================#

# CABLE CONFIGURATIONS
CABLE_NAME = ["DigilentHS1","UsbBlaster"]
PID = ["pid=0x6014","pid=0x6001"]
VID = ["vid=0x0403","vid=0x09fb"]

# CONFIGURATIONS FILES
STEPPINGS_FILE = "/STEPPINGS"
PARTS_FILE     = "/PARTS"
MANUFACTURERS_FILE = "/MANUFACTURERS"

# BASE DIRECTORY CONFIGURATION
BASE_FOLDER = "/usr/local/share/urjtag/"

# select the cable index
URJTAG_INDEX = 1

# ==================================================================#
#                       UTILITIES FUNCTIONS                         #
# ==================================================================#

# Function to print with elapsed time
def print_with_time(message):
    """
    Print Message with Elapsed Time

    Description:
    This function prints a message along with the elapsed time since a reference point (start_time). It is useful for tracking the time taken by specific operations in a script.

    Parameters:
    - message (str): The message to be printed with the elapsed time.

    Usage:
    1. Set the `start_time` variable before calling this function, typically at the beginning of a script or before the operation to be timed.
    2. Call this function with the desired message to print, and it will display the formatted message with the elapsed time.

    Note:
    - This function relies on the `time` module.
    - The elapsed time is formatted in seconds and milliseconds.

    """
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time)
    milliseconds = int((elapsed_time - seconds) * 1000)
    formatted_time = f"{seconds}.{milliseconds:03d}s"
    print(f"[{formatted_time}] {message}")


def get_device_id(urc, part_number, instruction_type):
    """
    Get the device ID for a specific part number and print the result.

    Args:
        urc: The urjtag chain object.
        part_number (int): The part number for which to retrieve the device ID.
        instruction_type (str): A string representing the type of instruction (e.g., "SAMPLE" or "EXTEST").

    Returns:
        int or None: The device ID if found, None otherwise.
    """
    try:
        device_id = urc.partid(part_number)
        print_with_time("{} DEVICE ID: {}".format(instruction_type, device_id))
    except:
        print_with_time("Device not found with part number: {}".format(part_number))
        return None
    return device_id


# convert the device id from decimal format to 32 bit binary
def decimal_to_32bit_binary(decimal_number):
    """
    Convert Decimal to 32-bit Binary Representation

    Description:
    This function takes a decimal number as input and converts it to a 32-bit binary representation. The result is a string containing the binary equivalent, padded with leading zeros if necessary.

    Parameters:
    - decimal_number (int): The decimal number to be converted.

    Returns:
    - str: A string representing the 32-bit binary equivalent of the input decimal number.

    """
    # Convert decimal to 32-bit binary representation
    return format(decimal_number, '032b')


# ==================================================================#
#                        URJTAG MANAGE                              #
# ==================================================================#


# Create chain object and connect to cable 
def get_urjtag_setup(cable_index):
    """
    Get urJTAG Setup for Cable Connection and Device Detection

    Description:
    This function establishes a connection to a JTAG cable using urJTAG library, performs cable testing, detects devices on the JTAG chain, and prints information about the connected devices. It returns the urjtag.chain() object for further use in JTAG operations.

    Parameters:
    - cable_index (int): Index specifying the cable to connect. It corresponds to the cable's name, PID (Product ID), and VID (Vendor ID) defined in the global constants.

    Returns:
    - urjtag.chain() object: The urJTAG chain object representing the connected JTAG chain and devices.

    """
    try:
        # Create a new urjtag chain object
        urc = urjtag.chain()
        # Connect to the specified cable using the given cable index
        urc.cable(CABLE_NAME[cable_index], PID[cable_index], VID[cable_index])
        print("Cable connected.")
        # Test the connected cable
        urc.test_cable()
        print("Cable test done.")
        # Detect devices on the chain
        urc.tap_detect()
        print("Device detection done.")
        # Print the chain length
        print("Chainlength={}".format(urc.len()))
        # Iterate through the chain and print the ID code for each device
        for i in range(0, urc.len()):
            idcode = urc.partid(i)
            print_with_time("IDCODE : [{}] 0x{:08x}".format(i, idcode))
        # Return the urc object
        return urc
    except Exception as e:
        # Handle exceptions if any and print an error message
        print("Failed to connect to cable: {} with PID: {}, VID: {}. Error: {}".format(
            CABLE_NAME[cable_index], PID[cable_index], VID[cable_index], str(e)))
        return None

# Try to set instruction on the active part in the chain
def urjtag_set_instruction(urc,part_no,instruction):
    """
    Set JTAG Instruction for a Specific Device in the Chain

    Description:
    This function sets the JTAG instruction for a specific device in the JTAG chain using the urJTAG library. It first selects the active part in the chain and then sets the provided instruction for the active part. The instruction is then shifted into the instruction register.

    Parameters:
    - urc (urjtag.chain() object): The urJTAG chain object representing the connected JTAG chain and devices.
    - part_no (int): The index of the device in the JTAG chain for which the instruction needs to be set.
    - instruction (str): The JTAG instruction to be set for the specified device.

    Returns:
    - bool: True if setting the instruction is successful, False otherwise.

    """
    if(DEBUG):
        print("DEBUG : ",end=" ")
        print("SET INSTRUCTION - {} in PART : {}".format(instruction,part_no))
    try:
        # Set the active part in the chain
        urc.part(part_no)
        # Set the instruction for the active part
        urc.set_instruction(instruction)
        # Shift the instruction register
        urc.shift_ir()
        return True
    except Exception as e:
        # Handle exceptions if any and print an error message
        print_with_time("Failed to set instruction on active part in the chain.\nPART: {}\nINSTRUCTION: {}\nError: {}".format(
            part_no, instruction, str(e)))
        return False


# ==================================================================#
#                       READ CONVERTED BSDL FILE                    #
# ==================================================================#

# get dictionary data from the bsdl converted file
def get_dictionary_from_bsdl(bsdl_file_path):
    """
    Extract Bit Information Dictionary from BSDL File

    Description:
    This function reads a BSDL (Boundary Scan Description Language) file and extracts information about each bit, creating a dictionary. The dictionary includes details such as IO type, safe value, pin name, control bit, disable value, and disable status for each bit.

    Parameters:
    - bsdl_file_path (str): The file path to the BSDL file to be processed.

    Returns:
    - dict: A dictionary containing bit information extracted from the BSDL file. The dictionary keys are bit numbers, and the values are dictionaries with detailed information.

    Note:
    - The BSDL file must follow the standard format for boundary scan description.
    - The function skips bits with pin name '*' and IO type OUTPUT/INPUT (O/I/B).

    """
    try:
        bit_info_dict = {}
        with open(bsdl_file_path, 'r') as bsdl_file:
            for line in bsdl_file:
                # get lines only starts with 'bit'
                if(line[:3] == 'bit'):
                    components = line.strip().split()
                    bit = int(components[1])
                    # if pin type is OUTPUT/INPUT (O/I/B) and pin name is '*' ignore the bits
                    if(components[4] != "*" and (components[2] == 'O' or components[2] == 'I' or  components[2] == 'B' )):
                        bit_info_dict[bit] = {
                        'io_type': components[2] ,
                        'safe_value': components[3],
                        'pin_name': components[4],
                        'control_bit': components[5] if len(components) > 5 else None,
                        'disable_value': components[6] if len(components) > 6 else None,
                        'disable_status': components[7] if len(components) > 7 else None,
                    }
                    elif(components[4] == "*" and (components[2] == 'C' )):
                       bit_info_dict[bit] = {
                        'io_type': components[2] ,
                        'safe_value': components[3],
                        'pin_name': components[4],
                        'control_bit': components[5] if len(components) > 5 else None,
                        'disable_value': components[6] if len(components) > 6 else None,
                        'disable_status': components[7] if len(components) > 7 else None, 
                    }   
        print_with_time("DICT file generated for {}".format(bsdl_file_path))
        if(DEBUG):
            print("DEBUG : > ")
            print_dict(bit_info_dict)
        return bit_info_dict
    except FileNotFoundError:
        print_with_time(f"File not found: {input_file_path}")
    except Exception as e:
        print_with_time(f"An error occurred: {e}")


# print dictionary data
def print_dict(dict_data):
    """
    Print Dictionary Key-Value Pairs with Elapsed Time

    Description:
    This function prints the key-value pairs of a dictionary along with the elapsed time since a reference point (start_time). It is useful for tracking the time taken to print dictionaries during script execution.

    Parameters:
    - dict_data (dict): The dictionary to be printed.
    """
    for key,value in dict_data.items():
        print_with_time("{} : {}".format(key,value))



# ==================================================================#
#                         PART FILE FETCH                           #
# ==================================================================#

# to find folder/file names from configurations files
def search_folders_by_device_id(device_id_part,file_path):
    """
    Retrieves information related to a specific part based on provided identifiers.

    Parameters:
    - device_id_part (str) : manufacture_id / parts_id / stepping_id
    - file_path (str): Base folder path where configuration files are located.

    Returns: 
    - str or None: The file name of the next file is identified by the given ID. Returns None if identifiers are not found or if there is an error (e.g., file not found).

    """
    try:
        with open(file_path,'r') as file:
            # split lines
            data = file.read().split("\n")
            for line in data:
                # split each line with tab seperation
                line_content = line.split('\t') 
                if(device_id_part in line_content):
                    # filter out unwanted characters and list items
                    info = [each.strip() for each in line_content if each != ""]
                    # fetch folder name
                    return info[1] if len(info) > 1 else None
        return None
    except FileNotFoundError:
        print_with_time(f"Error! : File not found: {file_path}")
        return None


def fetch_part_file(manufacture_id,parts_id,stepping_id,base_folder):
    """
    Retrieves information related to a specific part based on provided identifiers.

    Parameters:
    - manufacture_id (str): Identifier for the manufacturer.
    - parts_id (str): Identifier for the parts.
    - stepping_id (str): Identifier for the stepping.
    - base_folder (str): Base folder path where configuration files are located.

    Returns:
    - list or None: A list containing the manufacturer folder name, parts folder name, stepping folder name,
                   and the complete file path to the specified part configuration. Returns None if any of the
                   identifiers are not found or if there is an error (e.g., file not found).

    """
    # MANUFACTURERS file path
    content_file = base_folder + MANUFACTURERS_FILE
    # find manufacturer folder name
    manufacture_folder_name = search_folders_by_device_id(manufacture_id,content_file)
    if(manufacture_folder_name is None):
        print_with_time("Manufacturer name not present in the file : {}".format(content_file))
        return None
    # PARTS file path
    content_file = base_folder + manufacture_folder_name + PARTS_FILE
    # find parts folder name
    parts_folder_name = search_folders_by_device_id(parts_id,content_file)
    if(manufacture_folder_name is None):
        print_with_time("Parts name not present in the file : {}".format(content_file))
        return None
    # STEPPING file path
    content_file = base_folder + manufacture_folder_name + "/" + parts_folder_name + STEPPINGS_FILE 
    # find stepping folder name
    stepping_filename = search_folders_by_device_id(stepping_id,content_file)
    if(manufacture_folder_name is None):
        print_with_time("Parts file name not present in the file : {}".format(content_file))
        return None
    # generate parts filepath 
    content_file = base_folder + manufacture_folder_name + "/" + parts_folder_name + "/" + stepping_filename
    return [manufacture_folder_name,parts_folder_name,stepping_filename,content_file]



# ==================================================================#
#                        BITSTRING GENERATE                         #
# ==================================================================#

"""
bit [bit_value] [I/O/B/C] [safe_value/?] [pin_name/*] [control_bit/] [disable_value/] [disable_status/]
B - with control pin - need to set
O - with control pin - need to set 
O - without control pin  - no need to set


dict format : 
    key : 
        bitvalue
    values:
        io_type
        safe_value
        pin_name
        control_bit
        disable_value
        disable_status
"""

# set bit value
def set_bits(output_string,bit_position,bit_value):
    """
    Sets the value of a bit at a specified position in a given string.

    Parameters:
    - output_string (str): The original string in which the bit value needs to be set.
    - bit_position (int): The position of the bit to be set (0-indexed).
    - bit_value (int): The value (0 or 1) to set for the specified bit position.

    Returns:
    - str: A new string with the bit at the specified position set to the given value.

    """
    return output_string[:bit_position] + str(bit_value) + output_string[bit_position+1:]


def get_list_of_walkins_output_string(bit_info_dict,walkin_string,value):
    """
    Generates a list of modified output strings with only set output and control pins for walkin ones or zeros.

    Parameters:
    - bit_info_dict (dict): A dictionary containing bit information, including IO type, control bit, and disable/enable values.
    - walkin_string (str): The original walkin string representing the current state of bits.
    - value (int): The value (0 or 1) to set for the specified output bits.

    Returns:
    - list of str: A list of modified walkin strings with the specified output and control pins set to the given value.

    """
    dr_in_string_list = []
    for bit, info in sorted(bit_info_dict.items()):
        output_string = walkin_string[::-1]
        # only consider output pins
        if(info['io_type'] == 'O' or info['io_type'] == 'B'):
            # set output bit
            output_string = set_bits(output_string,bit,value)
            # If the control pin is specified, enable the pin by checking the enable value.
            if info['control_bit'] is not None:
                control_bit = int(info['control_bit'])
                if info['disable_value'] is not None:
                    disable_value = int(info['disable_value'])
                    enable_value = 1^disable_value
                    # set control bit
                    output_string = set_bits(output_string,control_bit,enable_value)
            dr_in_string_list.append(output_string[::-1])
    # generated bitstrings needs to be reversed , because urc.set_dr_in() function takes the string bits in reverse order.
    return dr_in_string_list
    

def get_walkin_zeros_or_once_setup_string(urc,bit_info_dict,value):
    """

    Generates a modified setup string for walkin zeros or ones based on the given bit information dictionary and value.

    Parameters:
    - urc (urjtag.chain() object): The urJTAG chain object representing the connected JTAG chain and devices.
    - bit_info_dict (dict): A dictionary containing bit information, including IO type, control bit, and disable/enable values.
    - value (int): The value (0 or 1) to set for the specified output bits.

    Returns:
    - str: A modified setup string for walkin zeros or ones with the specified output and control pins set to the given value.
    
    """
    output_string = urc.get_dr_in_string()
    for bit, info in sorted(bit_info_dict.items()):
        # only consider output pins
        if(info['io_type'] == 'O' or info['io_type'] == 'B'):
            # set output bit
            output_string = set_bits(output_string,bit,value^1)
            # If the control pin is specified, enable the pin by checking the enable value.
            if info['control_bit'] is not None:
                control_bit = int(info['control_bit'])
                if info['disable_value'] is not None:
                    disable_value = int(info['disable_value'])
                    enable_value = 1^disable_value
                    # set control bit
                    # if(value == 1):
                        # output_string = set_bits(output_string,control_bit,disable_value)
                    # else:
                    output_string = set_bits(output_string,control_bit,enable_value)
    # generated bitstrings needs to be reversed , because urc.set_dr_in() function takes the string bits in reverse order.
    return output_string[::-1]


# ==================================================================#
#                       BIT & CHANGES CHECK   - EXTEST              #
# ==================================================================#

def dr_out_changes_lookup(data_bits_old,data_bits_new,bsdl_dictionary,summary_dict,summary_dict_key):
    """
    Looks up and summarizes changes in the DR (Data Register) output bits.

    Parameters:
    - data_bits_old (str): The previous state of DR output bits.
    - data_bits_new (str): The new state of DR output bits.
    - bsdl_dictionary (dict): A dictionary containing BSDL (Boundary-Scan Description Language) information for each bit.
    - summary_dict (dict): A dictionary to store the summary of changes.
    - summary_dict_key (str): The key to use in the summary_dict to store the specific changes.

    Returns:
    - None
    
    Description:
    This function compares the old and new states of DR output bits and identifies differing bits. For each differing bit,
    it looks up the corresponding pin name from the provided BSDL dictionary and prints a summary of the change. Additionally,
    it updates the 'summary_dict' dictionary with the pin names and their corresponding changes. The 'walkin_state' is used to
    determine whether the bit change occurred during a walkin (shift) operation, and the summary is updated accordingly.

    """
    global walkin_state
    # summary
    summary_dict[summary_dict_key] = []
    summary_dict[summary_dict_key + "io"] = []
    differing_bits = [(i, data_bits_old[i], data_bits_new[i]) for i in range(len(data_bits_old)) if data_bits_old[i] != data_bits_new[i]]
    if(DEBUG):
        print("DEBUG : data bits old ",end="\n")
        print_with_time(data_bits_old)
        print("DEBUG : data bits new ",end="\n")
        print_with_time(data_bits_new)
        print("\n")
    for bit_info in differing_bits:
        print_with_time(f"Bit {bit_info[0]}: {bit_info[1]} -> {bit_info[2]}")
        if(bit_info[0] in bsdl_dictionary):
            pin_name = bsdl_dictionary[bit_info[0]]['pin_name']
            print_with_time(pin_name)
            # summary
            # walkin zero
            if(walkin_state == 0 and bit_info[1] == '1'):
                summary_dict[summary_dict_key].append(pin_name)
                summary_dict[summary_dict_key + "io"].append(f"{bit_info[1]} -> {bit_info[2]}")
            # walkin ones
            if(walkin_state == 1 and bit_info[1] == '0'):
                summary_dict[summary_dict_key].append(pin_name)
                summary_dict[summary_dict_key + "io"].append(f"{bit_info[1]} -> {bit_info[2]}")



def dr_shift_comapre(dr_init_bits,dr_bits_new,bsdl_dictionary,summary_dict,summary_dict_key):
    """
    Compares the changes in DR (Data Register) output bits during a shift operation.

    Parameters:
    - dr_init_bits (str): The initial state of DR output bits before the shift operation.
    - dr_bits_new (str): The new state of DR output bits after the shift operation.
    - bsdl_dictionary (dict): A dictionary containing BSDL (Boundary-Scan Description Language) information for each bit.
    - summary_dict (dict): A dictionary to store the summary of changes.
    - summary_dict_key (str): The key to use in the summary_dict to store the specific changes.

    Returns:
    - str: The updated state of DR output bits after the shift operation.
    """
    # compare the changes in dr out bits
    dr_out_changes_lookup(dr_init_bits,dr_bits_new,bsdl_dictionary,summary_dict,summary_dict_key)
    # keep last changes in dr bits 
    return dr_bits_new
    

def set_urc_bits(urc,bits_string_list,bit_info_dict,walkin_string,extest_part_number,sample_bsdl_dictionary,sample_part_number,dr_init_bits_sample):
    """
    Configures and performs EXTEST and SAMPLE operations using the provided URjtag instance.

    Parameters:
    - urc (urjtag.chain() object): The urJTAG chain object representing the connected JTAG chain and devices.
    - bits_string_list (list of str): A list of bit strings to set during EXTEST operations.
    - bit_info_dict (dict): A dictionary containing bit information, including IO type, control bit, and disable/enable values.
    - walkin_string (str): The initial state of DR (Data Register) output bits for walkin operations.
    - extest_part_number (str): The part number for EXTEST operations.
    - sample_bsdl_dictionary (dict): A dictionary containing BSDL (Boundary-Scan Description Language) information for SAMPLE operations.
    - sample_part_number (str): The part number for SAMPLE operations.
    - dr_init_bits_sample (str): The initial state of DR output bits for SAMPLE operations.

    Returns:
    - None
    
    """
    # summary of IO changes
    global summary_list
    dr_init_bits = walkin_string
    for bits_string in  bits_string_list:
        #summary
        summary_dict = {}
        print("---------------------------------------------------------------")
        #print_with_time( bits_string + "\n")
        urc.part(extest_part_number)
        urjtag_set_instruction(urc,extest_part_number,"EXTEST")
        urc.set_dr_in(bits_string)
        urc.shift_dr()
        print("\n--- EXTEST --- {}  --- {}\n".format(ALIAS_LIST[0],extest_part_number))
        dr_init_bits = dr_shift_comapre(dr_init_bits[::-1],bits_string[::-1],bit_info_dict,summary_dict,"extest")
        dr_init_bits = dr_init_bits[::-1]
        # sample run
        print("\n--- SAMPLE --- {}  --- {}\n".format(ALIAS_LIST[1],sample_part_number))
        urjtag_set_instruction(urc,sample_part_number,"SAMPLE/PRELOAD")
        dr_init_bits_sample = sample_run(urc,sample_bsdl_dictionary,dr_init_bits_sample,summary_dict,"sample")
        dr_init_bits_sample = dr_init_bits_sample[::-1]
        print("\n---------------------------------------------------------------")
        # summary
        summary_list.append(summary_dict)
    

# ==================================================================#
#                      BIT & CHANGES CHECK - SAMPLE                 #
# ==================================================================#


def get_sample_shift_init_bits(urc,sample_part_number):
    """
    Retrieves the initial state of DR (Data Register) output bits during a SAMPLE/PRELOAD shift operation.

    Parameters:
    - urc (urjtag.chain() object): The urJTAG chain object representing the connected JTAG chain and devices.
    - sample_part_number (str): The part number for SAMPLE operations.

    Returns:
    - str: The initial state of DR output bits during the SAMPLE/PRELOAD shift operation.

    Description:
    This function sets the instruction to SAMPLE/PRELOAD, shifts the DR bits, and retrieves the initial state of DR output bits
    during a SAMPLE/PRELOAD shift operation. It returns the obtained DR bits. If the instruction cannot be set, a message is printed,
    and the function returns None.
    
    """
    # get dr out bits
    status = urjtag_set_instruction(urc,sample_part_number,"SAMPLE/PRELOAD")

    if(status == False):
        print("Instruction canot set")
    urc.part(sample_part_number)    
    # shift dr bits
    urc.shift_dr()
    
    dr_bits = urc.get_dr_out_string()

    if(DEBUG):
        print("\nDEBUG : ",end=" ")
        print("DR SAMPLE INITIAL BITS inside function: {}".format(dr_bits))    
    return dr_bits


def sample_run(urc,bsdl_dictionary,dr_init_bits,summary_dict,summary_dict_key):
    """
    Performs a SAMPLE operation, retrieves the new state of DR (Data Register) output bits, and compares the changes.

    Parameters:
    - urc (urjtag.chain() object): The urJTAG chain object representing the connected JTAG chain and devices.
    - bsdl_dictionary (dict): A dictionary containing BSDL (Boundary-Scan Description Language) information for each bit.
    - dr_init_bits (str): The initial state of DR output bits before the SAMPLE operation.
    - summary_dict (dict): A dictionary to store the summary of changes.
    - summary_dict_key (str): The key to use in the summary_dict to store the specific changes.

    Returns:
    - str: The updated state of DR output bits after the SAMPLE operation.

    Description:
    This function performs a SAMPLE operation using the provided URJtag instance. It retrieves the new state of DR output bits
    and compares the changes with the initial state (`dr_init_bits`). The function then updates the 'summary_dict' dictionary
    with pin names and their corresponding changes during the SAMPLE operation. The resulting updated state of DR output bits
    is returned to be used for further comparisons.
    
    """
    # get dr out bits once again
    #urc.part(part_no)
    urc.shift_dr()
    dr_bits_new = urc.get_dr_out_string()

    return dr_shift_comapre(dr_init_bits[::-1],dr_bits_new[::-1],bsdl_dictionary,summary_dict,summary_dict_key)


# ==================================================================#
#                           SUMMARY FUNCTION                        #
# ==================================================================#

def view_summary():
    """
    Prints a summary of the changes in the global 'summary_list' by analyzing the EXTEST and SAMPLE operation results.

    Parameters:
    - None

    Returns:
    - None

    Description:
    This function analyzes the global 'summary_list', which contains dictionaries of changes resulting from EXTEST and SAMPLE
    operations. It constructs a 'summary_chain_dict' dictionary, associating EXTEST changes with corresponding SAMPLE changes.
    The function then prints a summary for each EXTEST pin, indicating whether it is connected, partially connected, or experiences
    interference during SAMPLE operations. The output provides insights into the impact of EXTEST changes on SAMPLE pins.
    
    """
    global summary_list
    # summary chain dictionary
    summary_chain_dict = {}
    print(LINE)
    print("------------------------- SUMMARY ---------------------------------")
    for summary_dict in summary_list:
        for index in range(len(summary_dict["extestio"])):
            # initialize summary chain dictionary - list
            if summary_dict["extest"][index] not in summary_chain_dict:
                summary_chain_dict[summary_dict["extest"][index]] = []

            if summary_dict["extestio"][index] == "0 -> 1":
                for sample_index in range(len(summary_dict["sampleio"])):
                    if summary_dict["sampleio"][sample_index] == "0 -> 1":
                        summary_chain_dict[summary_dict["extest"][index]].append(summary_dict["sample"][sample_index])

            elif  summary_dict["extestio"][index] == "1 -> 0":
                for sample_index in range(len(summary_dict["sampleio"])):
                    if summary_dict["sampleio"][sample_index] == "1 -> 0":
                        summary_chain_dict[summary_dict["extest"][index]].append(summary_dict["sample"][sample_index])


    for key, value in summary_chain_dict.items():
        print(f"{key} => ", end="")
        if len(value) == 2 and value[0] == value[1]:
            # Success: Exactly two identical items
            print(f"{value[0]}")
        elif len(value) > 2:
            # Partial: More than two items (Interference)
            print("Interference")
        elif len(value) == 1:
            # Partial: Only one item
            print("Partial")
        else:
            # Not connected: No items or more than two non-identical items
            print("Not connected")

    print(LINE)


# ==================================================================#
#                           MAIN FUNCTION                           #
# ==================================================================#

def command_line(argv):
    """
    CLI tool for executing URJTAG walkin along with sample operations.

    Parameters:
    - argv (list): Command-line arguments passed to the script.

    Returns:
    - None

    Description:
    This function defines a command-line interface (CLI) tool using argparse for executing the URJTAG walkin along
    with sample operations. It accepts various command-line arguments to customize the behavior of the tool.

    Command-Line Arguments:
    - --extest (int, default=0): Part number for EXTEST operations.
    - --extestalias (str): Alias value for EXTEST operations.
    - --sample (int, default=0): Part number for SAMPLE operations.
    - --samplealias (str): Alias value for SAMPLE operations.
    - --debug (int, default=0): Debug mode flag (1 for debug, 0 for normal mode).

    The function parses the command-line arguments, sets the debug mode if specified, and then calls the main function
    to execute the series of tests involving EXTEST and SAMPLE operations.

    Example Usage:
    python script.py --extest 123 --extestalias extest_device --sample 456 --samplealias sample_device --debug 1
    """
    parser = argparse.ArgumentParser(description='URJTAG walkin along with sample cli tool')

    # Add command-line arguments
    parser.add_argument('--extest', type=int, default=0, help='Description for extest argument')
    parser.add_argument('--extestalias', type=str, help='Description for extestalias argument')
    parser.add_argument('--sample', type=int, default=0, help='Description for sample argument')
    parser.add_argument('--samplealias', type=str, help='Description for samplealias argument')
    parser.add_argument('--debug', type=int, default=0, help='Description for extest argument')

    args = parser.parse_args()

    # Access the values of the command-line arguments
    # If no default value is specified, the variable will be None.
    extest_value = args.extest
    extest_alias_value = args.extestalias
    sample_value = args.sample
    sample_alias_value = args.samplealias
    debug  = args.debug

    global DEBUG
    DEBUG = (True if debug == 1 else False)

    if(DEBUG):
        print("DEBUG : ",end=" ")
        print(f"EXTEST: {extest_value}, EXTEST ALIAS: {extest_alias_value}, SAMPLE: {sample_value}, SAMPLE ALIAS: {sample_alias_value}")

    # execute main code
    main(extest_value,extest_alias_value,sample_value,sample_alias_value)




def main(extest_part_number,extest_alias_value,sample_part_number,sample_alias_value):
    """
    Main function to perform a series of tests involving EXTEST and SAMPLE operations on different devices,
    summarizing pin connections.

    Parameters:
    - extest_part_number (str): The part number for EXTEST operations.
    - extest_alias_value (str): The alias value for EXTEST operations.
    - sample_part_number (str): The part number for SAMPLE operations.
    - sample_alias_value (str): The alias value for SAMPLE operations.

    Returns:
    - None

    """
    global walkin_state
    global summary_list
    global URJTAG_INDEX

    # set alias for extest and sample from cli arguments
    ALIAS_LIST[0] = extest_alias_value
    ALIAS_LIST[1] = sample_alias_value

    # urjtag setup
    # param_0 : cable_index
    urc = get_urjtag_setup(URJTAG_INDEX)
    if urc is None:
        return

    # set instruction - EXTEST
    urjtag_set_instruction(urc,extest_part_number,"EXTEST")

    # Get device IDs for devices with sample and extest instructions
    sample_device_id = get_device_id(urc, sample_part_number, "SAMPLE")
    if sample_device_id is None:
        return

    extest_device_id = get_device_id(urc, extest_part_number, "EXTEST")
    if extest_device_id is None:
        return

    # binary representation of device id
    sample_device_id_binary = decimal_to_32bit_binary(sample_device_id)
    extest_device_id_binary = decimal_to_32bit_binary(extest_device_id)

    # STEPPINGS :  bits 31-28 of the Device Identification Register
    sample_stepping_id = sample_device_id_binary[:4]
    extest_stepping_id = extest_device_id_binary[:4]
    # PARTS : bits 27-12 of the Device Identification Register
    sample_parts_id = sample_device_id_binary[4:20]
    extest_parts_id = extest_device_id_binary[4:20]
    # MANUFACTURERS : bits 11-1 of the Device Identification Register
    sample_manufacture_id = sample_device_id_binary[20:31]
    extest_manufacture_id = extest_device_id_binary[20:31]

    print_with_time("---------- EXTEST DEVICE INFO ----------")
    print_with_time("PART NUMBER : {}".format(extest_part_number))
    print_with_time("DEVICE ID : {}".format(extest_device_id_binary))
    print_with_time("STEPPING ID : {}".format(extest_stepping_id))
    print_with_time("PARTS ID : {}".format(extest_parts_id))
    print_with_time("MANUFACTURES ID : {}".format(extest_manufacture_id))

    print_with_time("---------- SAMPLE DEVICE INFO ----------")
    print_with_time("PART NUMBER : {}".format(sample_part_number))
    print_with_time("DEVICE ID : {}".format(sample_device_id_binary))
    print_with_time("STEPPING ID : {}".format(sample_stepping_id))
    print_with_time("PARTS ID : {}".format(sample_parts_id))
    print_with_time("MANUFACTURES ID : {}".format(sample_manufacture_id))


    # fetch part files
    sample_part_file = fetch_part_file(sample_manufacture_id,sample_parts_id,sample_stepping_id,BASE_FOLDER)
    if(sample_part_file is not None):
        print_with_time("SAMPLE/PRELOAD FILE INFO : {}".format(sample_part_file))

    extest_part_file = fetch_part_file(extest_manufacture_id,extest_parts_id,extest_stepping_id,BASE_FOLDER)
    if(extest_part_file is not None):
        print_with_time("EXTEST FILE INFO : {}".format(extest_part_file))

    # get bit_info_dict from converted bsdl file
    sample_bit_info_dict = get_dictionary_from_bsdl(sample_part_file[3])
    extest_bit_info_dict = get_dictionary_from_bsdl(extest_part_file[3])

    input("\n\nDo you want to continue with the test ? Press enter key to continue\n")
    
    try:
        while True:
            print(LINE)

            # set EXTEST instruction
            urjtag_set_instruction(urc,extest_part_number,"EXTEST")

            print("\n=======> WALKIN ZEROS SETUP...")
            walkin_zero_string =  get_walkin_zeros_or_once_setup_string(urc,extest_bit_info_dict,0)
            if(DEBUG):
                print("DEBUG : ",end=" ")
                print_with_time(walkin_zero_string)

            print("\n=======> WALKIN ONES SETUP...")
            walkin_ones_string =  get_walkin_zeros_or_once_setup_string(urc,extest_bit_info_dict,1)
            if(DEBUG):
                print("DEBUG : ",end=" ")
                print_with_time(walkin_ones_string)

            print("\n=======> WALKIN ZEROS LOOP...")
            #input("\nPress enter key to continue\n")
            urc.set_dr_in(walkin_zero_string)
            urc.shift_dr()
            print_with_time("WALKIN ZEROS initial value should turn off all LEDs on or IO to 1 now")
            
            dr_init_bits_sample = get_sample_shift_init_bits(urc,sample_part_number)
            #print(dr_init_bits_sample)
            if(DEBUG):
                print("\nDEBUG : ",end=" ")
                print("DR SAMPLE INITIAL BITS returned from function: ".format(dr_init_bits_sample))
            walkin_zero_output_list =  get_list_of_walkins_output_string(extest_bit_info_dict,walkin_zero_string,0)
            # flag set for summary chain
            walkin_state = 0
            set_urc_bits(urc,walkin_zero_output_list,extest_bit_info_dict,walkin_zero_string,extest_part_number,sample_bit_info_dict,sample_part_number,dr_init_bits_sample)
            input("\nPress enter key to continue\n")

            print("\n=======> WALKIN ONES LOOP...")
            input("\nPress enter key to continue\n")
            urjtag_set_instruction(urc,extest_part_number,"EXTEST")
            urc.set_dr_in(walkin_ones_string)
            urc.shift_dr()
            print_with_time("WALKIN ONES initial value set;It should turn off all LEDs off or IO to zero now")
            input("\nPress enter key to continue\n")
            dr_init_bits_sample = get_sample_shift_init_bits(urc,sample_part_number)
            walkin_ones_output_list =  get_list_of_walkins_output_string(extest_bit_info_dict,walkin_ones_string,1)
            # flag set for summary chain
            walkin_state = 1
            set_urc_bits(urc,walkin_ones_output_list,extest_bit_info_dict,walkin_ones_string,extest_part_number,sample_bit_info_dict,sample_part_number,dr_init_bits_sample)

            input("\nPress enter key to view summary\n")
            # to view sumamry of IO pin changes
            view_summary()
            # reset summary list
            summary_list = []
            input("\nPress enter key to continue\n")

    except KeyboardInterrupt:
            print_with_time("Loop interrupted by user")
            #urc_extest.reset
            urc.reset


# ==================================================================#
#                           EXECUTION STARTS                        #
# ==================================================================#   

if __name__ == "__main__":
    command_line(sys.argv)

    
