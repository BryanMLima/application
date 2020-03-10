import os, hashlib
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from Crypto.PublicKey import RSA

app = Flask(__name__)
# Create folders to help separate files per funcionality
os.makedirs(os.path.join(app.instance_path, 'hashcode'), exist_ok=True)

@app.route('/')
def home():  
    return render_template('index.html') 

@app.route('/readfile')  
def read():  
    return render_template('upload.html')

@app.route('/hashcode', methods = ['POST'])  
def hashcode():  
    if request.method == 'POST':
        f = request.files['file']
        # returns the hashcode from the file sent
        hashcode = hash_function(f)
        return render_template('content.html', text = hashcode)

@app.route('/generate_keys', methods = ["POST", "GET"])
def keys_option():
    if request.method == 'POST':
        path_to_keys = os.path.join(app.instance_path, 'keys')
        size = request.form.get('size', type = int) 
        key = RSA.generate(size)
        private_key = key.exportKey()
        file_out = open(path_to_keys+"/private.pem","wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open(path_to_keys+"/receiver.pem", "wb")
        file_out.write(public_key)

        return render_template("content.html", text = public_key)
    else:
        return render_template("generate_keys.html")

def hash_function(f):
    BLOCK_SIZE = 65536
    # Absolute path to file
    file = os.path.join(app.instance_path, 'hashcode', secure_filename(f.filename))
    f.save(file)
    file_hash = hashlib.sha256()
    # Read the file in chunks to use less RAM for the process
    with open(file, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            # Update the hash object
            file_hash.update(fb) 
            fb = f.read(BLOCK_SIZE)
    return file_hash.hexdigest()
    
if __name__ == '__main__':  
    app.run(debug = True)