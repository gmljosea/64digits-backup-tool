"""
Script for downloading a 64digits user's entire blog page and file manager.

Write a credentials.json file with the following contents:

{
    "username": "your username",
    "password": "your password"
}

If you have customized your CSS, this script will probably blow up.

This creates a local directory 'blogs' with an .html file for each blog. If you
want to preserve comments aswell, configure your 64digits account so it always
shows all comments.

It also creates a blogs.json file with all the blogs information saved in a more
structured way. Blogs are saved as an array of objects with the keys "id",
"title", "date" and "content". The date is parsed and converted to ISO format.

This also creates a local directory 'files' which contains a backup of all
files found in the file manager. Their timestamps are modified to match the
server's.
"""
import datetime
import json
import os
import re
import argparse

import pyquery
import requests

with open("credentials.json") as f:
    credentials = json.load(f)
    USERNAME = credentials["username"]
    PASSWORD = credentials["password"]

DATE_FORMAT = "Posted on %B %d, %Y at %H:%M"
FILEMAN_DATE = "%d/%m/%Y %I:%M:%S %p"


def authenticated_session():
    s = requests.Session()
    auth = {
        "login_cmd": 1,
        "username": USERNAME,
        "password": PASSWORD
    }
    s.post("http://www.64digits.com/index.php", data=auth)
    return s


def pull_blogs(session):
    """Fetch all blogs and dump each into an .html file"""
    page_number, blog_urls, blogs = 0, [], []

    while True:
        print("Pulling page ", page_number)

        page = session.get(
            "http://64digits.com/users/index.php",
            params={"userid": USERNAME, "page": page_number}
        )
        pq = pyquery.PyQuery(page.text)

        pq(".blog_wrapper")
        blog_urls += list(map(
            lambda x: x.get("href"),
            pq(".blog_wrapper a.fntblue.fnt12,fntbold")
        ))

        if pq(".lnkdec")[-1].text_content().strip() == "Next Page":
            page_number += 1
        else:
            break

    os.makedirs("blogs", exist_ok=True)

    for url in blog_urls:

        blog_id = re.search(r"id=(\d+)$", url).group(1)
        url = "http://64digits.com/users/" + url

        print("Processing blog at", url)
        blog = session.get(url)

        pq = pyquery.PyQuery(blog.text)

        title, date = pq(".blog_wrapper > div:first > div:first > span")[:2]
        title = title.text_content().strip()
        date = datetime.datetime.strptime(date.text_content().strip(), DATE_FORMAT).isoformat()
        content = pyquery.PyQuery(pq(".blog_wrapper > div:first > div")[1]).html()

        blogs.append({
            "id": blog_id,
            "title": title,
            "date": date,
            "content": content
        })

        # Save full HTML dump, including comments
        if title is None:
            print(url)

        filename = "%s.html" % title.replace("/", '').replace("\\", '')
        with open(os.path.join("blogs", filename), mode="w") as f:
            f.write(blog.text)

    with open("blogs.json", mode="w") as f:
        json.dump(blogs, f, indent=2)


def backup_filemanager(session):
    os.makedirs("files", exist_ok=True)
    fileman = session.get(
        "http://www.64digits.com/users/index.php",
        params={"userid": USERNAME, "cmd": "file_manager"}
    )
    pq = pyquery.PyQuery(fileman.text)
    urls = pq("a.file")
    for url in urls:
        date_td = url.getparent().getnext().getnext()
        date = date_td.text_content().strip() + " " + date_td.getnext().text_content().strip()
        url = url.get("href")
        print("Backing up file", url)
        date = datetime.datetime.strptime(date, FILEMAN_DATE).timestamp()
        filename = re.search(".*/(.*)", url).group(1)
        r = session.get(url)
        file_path = os.path.join("files", filename)
        with open(file_path, mode="wb") as f:
            f.write(r.content)
        os.utime(file_path, times=(date, date))


def main(args):
    session = authenticated_session()
    pull_blogs(session)
    if not args.skip_files:
        backup_filemanager(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backup 64Digits user blogs and files.')
    parser.add_argument('-s', '--skip-files', action="store_true", help="don't backup filemanager contents")
    main(parser.parse_args())
