import secrets
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Generate a random secret key
secret_key = secrets.token_hex(16)  # Generate a 32-character hexadecimal string (16 bytes)
print(secret_key)

# Set the secret key for the Flask application
app.secret_key = secret_key
