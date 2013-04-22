Blog-Comment-Counter
====================
1. Install Python 2.7 (32-bit version)

2. Install [setuptools (32-bit version)](https://pypi.python.org/pypi/setuptools#files)

3. Install the Google Blogger API library, by running `easy_install --upgrade google-api-python-client`

4. In terminal run `easy_install gspread`
this installs the library that helps access googleDocs

5. Download from github the code, should have `comment_counter.py` and `rfc3339.py`

6. Put your gmail that access the google doc in `google_account.txt`

7. Put your password inside `google_password.txt`

8. Download attached `private_key.txt` from email and put in same folder as all the rest of this (this is a private key from Google that gives metered access to bloggerAPI, do not share or post publically.)

9. Open `comment_counter.py` and update `wks_name` (name of the googleDoc), `sem_start` (date of first class of semester), `sem_end` (date of last day of the semester)

10. Run `python comment_counter.py`
