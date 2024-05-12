# Flask LSB Steganography Application

This is a Flask web application that allows users to perform Least Significant Bit (LSB) steganography on image files. LSB steganography involves hiding information within the least significant bits of image pixels, allowing for secret communication within images.

## Features

- **User Authentication**: Users can sign up and log in to the application to access its features securely.
- **LSB Embedding**: Users can upload an image file and a message file, and the application will embed the message into the image using LSB steganography.
- **LSB Extraction**: Users can upload an embedded image file, and the application will extract the hidden message using LSB steganography.
- **File Upload and Download**: Uploaded files are stored securely on the server, and users can download the embedded images or extracted messages.

## Installation

1. Clone this repository to your local machine:
   git clone <https://github.com/aryanmainkar/Steganography-Website.git>
   
2. Install the required Python packages:
   pip install -r requirements.txt

3. Set up Firebase Authentication:

   - Create a Firebase project and download the service account credentials JSON file.
   - Rename the downloaded JSON file to `firebaseauth.json` and place it in the project directory.
  

4. Access the application in your web browser at `http://localhost:5000`.
5. Run the Flask application:
   python app.py 

## Usage

1. Sign up for an account or log in if you already have one.
2. Upload an image file and a message file for embedding or an embedded image file for extraction.
3. Set the LSB embedding parameters (start bit, periodicity, skip bits) if embedding.
4. Click the "Submit" button to perform LSB embedding or extraction.
5. Download the resulting image or view the extracted message.

## Contributing

Contributions are welcome! Please feel free to fork this repository and submit pull requests to contribute new features, enhancements, or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


