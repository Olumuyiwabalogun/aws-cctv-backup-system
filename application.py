from flask import Flask, render_template, request, redirect, url_for, session, send_file
import boto3
import os
from dotenv import load_dotenv  # Import dotenv to load environment variables

# Load environment variables from .env file
load_dotenv()

application = Flask(__name__, template_folder='templates')

# Secret key for session management
application.secret_key = os.getenv("SECRET_KEY")

# AWS Config (Loaded from .env)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = 'semcloudnvr'  # Keeping this hardcoded

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# User credentials
users = {"admin": "password123", "user": "mypassword"}

@application.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username  # Store user in session
            return redirect(url_for("s3_files"))  # Redirect to files page
        else:
            return render_template("index.html", error="Invalid username or password")

    return render_template("index.html")

@application.route("/dashboard")
def dashboard():
    if "user" in session:                            
        return render_template("dashboard.html")
    return redirect(url_for("index"))

@application.route('/files/')
@application.route('/files/<path:folder>')
def s3_files(folder=""):
    if 'user' not in session:  # Ensure user is logged in
        return redirect(url_for('index'))
    
    # List objects in the specified folder
    prefix = folder + "/" if folder else ""  # Ensure correct folder path
    objects = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)

    files = []
    folders = set()

    for obj in objects.get('Contents', []):
        key = obj['Key']
        relative_key = key[len(prefix):]  

        if '/' in relative_key:  
            folder_name = relative_key.split('/')[0]  
            folders.add(folder_name)
        else:
            files.append(relative_key)  

    return render_template('files.html', files=files, folders=sorted(folders), current_folder=folder)

@application.route('/download/<path:filename>')
def download_file(filename):
    if 'user' not in session:  
        return redirect(url_for('index'))

    #  Download directory
    download_dir = os.path.join(os.getcwd(), 'downloads', os.path.dirname(filename))  
    os.makedirs(download_dir, exist_ok=True)  # Ensure folder structure exists

    # Safe file path
    safe_filename = os.path.basename(filename).replace(" ", "_")  # Remove directory structure from filename
    file_path = os.path.join(download_dir, safe_filename)

    try:
        s3.download_file(S3_BUCKET_NAME, filename, file_path)  # Download the file
        return send_file(file_path, as_attachment=True)  # Send file to user
    except Exception as e:
        return f"Error downloading file: {str(e)}"

@application.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))  # Redirect to login page

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=False)
