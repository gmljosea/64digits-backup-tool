## 64Digits Backup Tool

A script for downloading a 64digits user's entire blog page and file manager.

### Requirements

- Python 3 (probably, didn't test with 2.7)
- requests
- pyquery

### Usage

Install the required libraries. In linux you can do:

    sudo pip3 install -r requirements.txt

Write a credentials.json in the same directory as pull.py with the following contents:

    {
        "username": "your username",
        "password": "your password"
    }

Then run

    python3 pull.py


### Results

This creates a local directory 'blogs' with an .html file for each blog. If you
want to preserve comments aswell, configure your 64digits account so it always
shows all comments.

It also creates a blogs.json file with all the blogs information saved in a more
structured way. Blogs are saved as an array of objects with the keys "id",
"title", "date" and "content". The date is parsed and converted to ISO format.

This also creates a local directory 'files' which contains a backup of all
files found in the file manager. Their timestamps are modified to match the
server's.

### Caveats

If you have customized your CSS, this script will probably blow up.
