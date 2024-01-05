import requests
import argparse

def post_image(payload):
    try:
        url = 'http://localhost:5000/images'

        if "file" in payload:
            response = requests.post(url, files=payload)
        else:
            response = requests.post(url, json=payload)

        return response
    except Exception as ex:
        print(f"Uncaught Exception: {ex}")

def main():
    parser = argparse.ArgumentParser(description='A simple command-line argument parser for sending images.')
    
    # Adding arguments
    parser.add_argument('-p', '--path', type=str, help='url or local location of valid image')
    parser.add_argument('-l', '--label', type=str, help='label for image')
    parser.add_argument('-f', '--file', type=str, help='local location of valid image posted via file')
    parser.add_argument('-d', '--detect', action='store_true', help='Flag for triggering detection')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag for verbose printing')

    # Parsing arguments
    args = parser.parse_args()

    payload = {
        "detect": args.detect
    }

    if args.path or args.label or args.file:
        # Accessing arguments
        if args.path:
            payload['path'] = args.path
        if args.label:
            payload['label'] = args.label
        
        # If the file option is filled out, just send the entire file
        # and overwrite other options
        if args.file:
            payload = {
                "file": open(args.file, 'rb')
            }
        if args.verbose:
            print(payload)
        response = post_image(payload)
        print(response.status_code)
        if args.verbose:
            print(response.json())
    else:
        print("Add path, or file of image to use this script! Use --help for details")

if __name__ == "__main__":
    main()
