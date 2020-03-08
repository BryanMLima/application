import os
from hashcode import encrypt_string
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)  

@app.route('/')
def index():  
    return render_template("index.html") 

@app.route('/readfile')  
def read():  
    return render_template("upload.html")
    
@app.route('/hashcode', methods = ['POST'])  
def hashcode():  
    if request.method == 'POST':
        # Save file to read, then delete it
        f = request.files['file']  
        f.save(f.filename)
        file = open(f.filename, "r")
        content = file.read()
        file.close()
        os.remove(f.filename)
        hash_code = encrypt_string(content)
        return render_template("content.html", text = hash_code)
    
if __name__ == '__main__':  
    app.run(debug = True)   