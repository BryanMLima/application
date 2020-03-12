import os, hashlib
import fnmatch
import random
from OpenSSL import crypto, SSL
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from Crypto.PublicKey import RSA

app = Flask(__name__)
# Create folders to help separate files per funcionality
os.makedirs(os.path.join(app.instance_path, "hashcode"), exist_ok=True)
# Create folder to store keys
path_to_keys = os.path.join(app.instance_path, "keys")
path_to_ca_root = os.path.join(app.instance_path, "ca_root")

@app.route("/")
def home():  
    return render_template("index.html") 

@app.route("/readfile")  
def read():  
    return render_template("upload.html")

@app.route("/hashcode", methods = ["POST"])  
def hashcode():  
    if request.method == "POST":
        f = request.files["file"]
        # returns the hashcode from the file sent
        hashcode = hash_function(f)
        return render_template("content.html", text = hashcode)

@app.route("/generate_keys", methods = ["POST", "GET"])
def keys_option():
    if request.method == "POST":
        # Sets the size of the RSA Key
        size = request.form.get("size", type = int) 
        key = RSA.generate(size)
        private_key = key.exportKey()
        # Files with the same name
        existing_files = fnmatch.filter((f for f in os.listdir(path_to_keys)), "private_*.pem")
        filename = path_to_keys + "/private_key_%d.pem" % (len(existing_files) + 1)
        file_out = open(filename,"wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        existing_files = fnmatch.filter((f for f in os.listdir(path_to_keys)), "public_*.pem")
        filename2 = path_to_keys + "/public_key_%d.pem" % (len(existing_files) + 1)
        file_out = open(filename2, "wb")
        file_out.write(public_key)

        return render_template("keys_generated.html")
    else:
        return render_template("generate_keys.html")

@app.route("/keys_generated")
def keys_generated():
    return render_template("keys_generated.html")

@app.route("/certificates", methods = ["POST", "GET"])
def create_root_ca():
    # if request.method == "POST":
    # generate key
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # Creating a self signed certificate
    certificate = crypto.X509()
    certificate.get_subject().CN = "Common Name"
    certificate.set_serial_number(random.randint(1000000000, 1000000000))
    certificate.set_issuer(certificate.get_subject())
    certificate.sign(k, "sha256")

    open(path_to_ca_root+"/certificate.crt", "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
    open(path_to_ca_root+"/ca_private_key.pem", "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

    return render_template("generate_keys.html")
    # else:
    #     return render_template("certificates.html")

def hash_function(f):
    BLOCK_SIZE = 65536
    # Absolute path to file
    file = os.path.join(app.instance_path, "hashcode", secure_filename(f.filename))
    f.save(file)
    file_hash = hashlib.sha256()
    # Read the file in chunks to use less RAM for the process
    with open(file, "rb") as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            # Update the hash object
            file_hash.update(fb) 
            fb = f.read(BLOCK_SIZE)
    return file_hash.hexdigest()
    
if __name__ == "__main__":  
    app.run(debug = True)