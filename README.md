# NAMA app
Application for importing a TSV file of sales, storing the content in a database, and then display its data to the user that uploaded the file.
It was developed in Python 3.8.

## Starting/installing the app:
In terminal, inside the /app directory, execute the commands:
```bash
pip install -r ../requirements.txt

# Use the location you want to create de database.
# In this case was used the '/tmp' directory.
export SQLALCHEMY_DATABASE_URI=sqlite:////tmp/nama.db

#the folder to store uploaded files. '/tmp' selected 
export UPLOAD_FOLDER=/tmp

# Creates database and tables
python3 -c 'from app import db; db.create_all()'

export FLASK_APP=app
flask run
```

## Testing the app:
In terminal, inside the /app directory, execute the commands:
```bash
pytest ../tests/
```
