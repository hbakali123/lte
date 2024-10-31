import os
import requests
import subprocess
from io import BytesIO
import gzip
import tempfile

# Lambda handler: entry point for function when an API call is made
def lambda_handler(event, context):
    # Extracting the serial number and part number from the incoming API request
    serial_num = event['queryStringParameters']['serial']
    part_num = event['queryStringParameters'].get('partnum', 'L001')  # Default to L001 if partnum is not provided
    
    # Process images for the LTE Node
    if part_num == 'L001':
        # If the part number is L001 (LTE Node), call the function that handles this
        return handle_lte_node(serial_num)
    else:
        # If the part number is not supported, return an error
        return {
            'statusCode': 400,
            'body': 'Unsupported part number'
        }

#function handles the programming and image flashing for L001
def handle_lte_node(serial_num):
    # first Program  Initial Image (IMEI/Serial provisioning)
    result = program_image('LTE_Node_Init.hex')  # Calls function to program initial image
    if not result:
        # If there's an error during programming, then return a failure response
        return {
            'statusCode': 500,
            'body': 'Error programming initial image'
        }

    #second, Fetch IMEI from the device , how will the device give the IMEI????
    imei = fetch_imei_from_device(serial_num)  # Mock function to simulate fetching IMEI

    #third,  Associate IMEI with the Serial Number by calling Waites Server API
    response = associate_imei_with_serial(serial_num, imei)
    if response.status_code != 200:
        # If the API call fails, return a failure response with the API error message
        return {
            'statusCode': 500,
            'body': f"Error associating IMEI {imei} with Serial {serial_num}: {response.text}"
        }
    
    #fourth,  Program the Production Image (main application firmware)
    result = program_image('LTE_Node_App.hex')  # Calls function to program production image
    if not result:
        # If there's an error during programming the production image, return failure response
        return {
            'statusCode': 500,
            'body': 'Error programming production image'
        }

    # If all the steps succeed, return a success message
    return {
        'statusCode': 200,
        'body': 'Successfully programmed both images and associated IMEI'
    }

# Function to program the image (this will execute a system command to flash the image onto the device)
def program_image(image_name):
    try:
        # Set up environment variables for system command
        env = dict(os.environ)
        # Command to run the flashing process
        cmds = [os.path.join(tempfile.gettempdir(), "commander", "commander"), "convert", image_name]
        # Execute command and capture the output
        result = subprocess.check_output(cmds, stderr=subprocess.STDOUT, env=env)
        print(result)  # Print the output for debugging purposes
        return result  # Return the output if the command succeeds
    except subprocess.CalledProcessError as err:
        # If there's an error during the command execution, print and return None
        print(f"Error programming image: {err.output}")
        return None

# Function to fetch IMEI from the device (PLACEHOLDER !!!! need to replace it with actual logic)
def fetch_imei_from_device(serial_num):
    # need to write logic that interacts with the device to fetch the IMEI
    imei = "123456789012345"  # PLACEHOLDER -- thhis IMEI is just for show!!!
    return imei

# Function to associate IMEI with Serial Number by making a POST request to Waites API
def associate_imei_with_serial(serial_num, imei):
    #URL of  API that will associate the IMEI with the Serial Number -- PLACEHOLDER
    url = 'https://waites-server/fetch-imei'
    #data to send in the POST request
    data = {
        'serial_number': serial_num,
        'imei': imei
    }
    # Send the POST request and return the response
    response = requests.post(url, json=data)
    return response