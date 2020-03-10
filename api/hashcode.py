import os, hashlib
from werkzeug.utils import secure_filename

def hash_function(f):
    # Absolute path to file
    path_to_file = os.path.join(app.instance_path, 'hashcode', secure_filename(f.filename))
    # Save file to read, then delete it
    f.save(path_to_file)
    file = open(path_to_file, "r")
    content = file.read()
    file.close()
    os.remove(path_to_file)
    # use the sha256 algorithm on file
    sha_signature = \
        hashlib.sha256(content.encode()).hexdigest()
    return sha_signature