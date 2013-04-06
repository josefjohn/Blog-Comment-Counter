# Authors: Gautam Jain & Josef John

import math
import pprint
import gspread
import rfc3339
from apiclient.discovery import build
from urlparse import urlparse
from datetime import datetime

# Record script start time
script_start = datetime.now()

# Google Docs Worksheet Info
wks_name = 'Test Spreadsheet'

# Semester dates
sem_start = '2013-01-28'  # Must be a Monday
sem_end = '2013-05-05'    # Must be a Sunday

sem_start = rfc3339.strtotimestamp(sem_start + 'T00:00:00-08:00')
sem_end = rfc3339.strtotimestamp(sem_end + 'T23:59:59-07:00')

week_in_seconds = 604800

# Convert times to RFC3339 format as required by Blogger API
sem_start_rfc3339 = rfc3339.timestamptostr(sem_start)
sem_end_rfc3339 = rfc3339.timestamptostr(sem_end)

# The private API key is stored in a separate file.
api_key = open('private_key.txt').readline()

# The apiclient.discovery.build() function returns an instance of an API service
# object that can be used to make API calls. The object is constructed with
# methods specific to the blogger API. The arguments provided are:
#   name of the API ('blogger')
#   version of the API you are using ('v3')
#   API key
blogger = build('blogger', 'v3', developerKey=api_key)

## Read credentials from txt file, and login with your Google account
ga = open('google_account.txt').readline()
gp = open('google_password.txt').readline()
gc = gspread.login(ga, gp)


# Returns the a list of blog URLs from the Google Docs
def get_blog_URLs():
    # Connect to Google Docs spreadsheet and get column with header 'Blog_URL'
    wks = gc.open(wks_name).sheet1
    url_header_cell = wks.find('Blog_URL')
    blog_URLs_list = wks.col_values(url_header_cell.col)

    # Filter through URLs to remove any non-Blogger entries
    blog_URLs_list = filter(is_blogger_URL, blog_URLs_list)

    return blog_URLs_list


# Returns a boolean depending if URL is a Blogger/Blogspot URL
def is_blogger_URL(url):
    return url is not None and 'blogspot.com' in url


# Returns the blog ID for the given blog URL
def get_blog_id(blog_url):
    response = blogger.blogs().getByUrl(
        url=format_url(blog_url),
        fields="id").execute()
    return str(response['id'])


# Returns a formatted URL with 'http://'' prefix if does not already exist
def format_url(url):
    if not urlparse(url).scheme:
        url = "http://" + url
    return url


# Returns a list of post IDs for the given blog that were
# published between sem_start and sem_end
def get_posts(blog_id):
    post_ids = []
    page_token = ''
    while True:
        # Request a list of posts between specified dates. Only return post IDs.
        if (page_token == ''):
            response = blogger.posts().list(
                blogId=blog_id,
                startDate=sem_start_rfc3339,
                endDate=sem_end_rfc3339,
                maxResults=10,
                fields='items/id,nextPageToken').execute()
        else:
            response = blogger.posts().list(
                blogId=blog_id,
                startDate=sem_start_rfc3339,
                endDate=sem_end_rfc3339,
                pageToken=page_token,
                maxResults=10,
                fields='items/id,nextPageToken').execute()

        # Reformat response into a list
        for post in response.get('items', []):
            post_ids.append(str(post['id']))

        page_token = str(response.get('nextPageToken'))

        # Check if there are no more 'pages'
        if page_token == 'None':
            break

    return post_ids


# Returns a list of comments for the given blog and post that were
# published between sem_start and sem_end.  Comments are dictionaries
# with the following keys: author_id, author_name, comment_id, publish_date
def get_comments(blog_id, post_id):
    # Request a list of comments between specified dates with specified fields.
    response = blogger.comments().list(
        blogId=blog_id,
        postId=post_id,
        startDate=sem_start_rfc3339,
        endDate=sem_end_rfc3339,
        fields='items(author(displayName,id),id,published)').execute()

    # Reformat response into a list
    comments = []

    for comment in response.get('items', []):
        try:
            comments.append({
                'author_id': str(comment['author']['id']),
                'author_name': str(comment['author']['displayName']),
                'comment_id': str(comment['id']),
                'publish_date': str(comment['published'])})
        except KeyError:
            print 'Invalid comment detected.'

    return comments


# Returns a list of all comments for the give blog that
# were published between sem_start and sem_end
def get_all_comments(blog_id):
    posts = get_posts(blog_id)
    comments = []

    for post in posts:
        comments += get_comments(blog_id, post)

    return comments


def get_author(blog_id, post_id):
    response = blogger.posts().get(
        blogId=blog_id,
        postId=post_id,
        fields='author/id').execute()

    return str(response.get('author')['id'])


#returns list of dictionaries
#each dictionary maps to a week
#each dictionary contains author_id keys mapping to a set of comment_ids for that week
#for each dictionary, keys are author_id, values are sets of the comments
#call len(dict[author_id]) to get comments for a given week
def get_total_comments(blog_ids):
    # Initialize dictionaries
    total_comments_dictionary_for_week = []
    for i in range(0, get_week(sem_end_rfc3339)):
        total_comments_dictionary_for_week.append(dict())

    # Iterate through all blogs
    for blog_id in blog_ids:
        post_ids = get_posts(blog_id)

        # Request and save author ID for later use
        #blog_authors_dict[get_author(blog_id, post_ids[0])] = blog_id
        blog_authors_dict[blog_id] = get_author(blog_id, post_ids[0])

        # Iterate through every post
        for post_id in post_ids:
            list_of_comments_dict = get_comments(blog_id, post_id)

            # Iterate through every comment
            for comment in list_of_comments_dict:
                author_id = comment['author_id']
                comment_id = comment['comment_id']
                publish_date = comment['publish_date']
                week = get_week(publish_date)
                print str(week),

                week_comments_dict = total_comments_dictionary_for_week[week]

                if author_id not in week_comments_dict.keys():
                    week_comments_dict[author_id] = []
                
                week_comments_dict[author_id].append(comment_id)

    return total_comments_dictionary_for_week


def get_week(publish_date_rfc3339):
    publish_date = rfc3339.strtotimestamp(publish_date_rfc3339)
    return int(math.floor((publish_date - sem_start) / week_in_seconds))


#################################################

blog_URLs = get_blog_URLs()

blog_IDs_dict = {}
blog_authors_dict = {}

for blog_URL in blog_URLs:
    blog_ID = get_blog_id(blog_URL)
    blog_IDs_dict[blog_URL] = blog_ID

print '######### BLOG_URL -> BLOG_ID'
pprint.pprint(blog_IDs_dict)

print '######### PROCESSED DATA'
data = get_total_comments(blog_IDs_dict.itervalues())

print '######### BLOG_ID -> AUTHOR_ID'
pprint.pprint(blog_authors_dict)


# Write to Google Docs Spreadsheet
wks = gc.open(wks_name).sheet1

url_header_col = wks.find('Blog_URL').col
week1_col = wks.find('Week_1').col

for row in range(1, len(wks.col_values(url_header_col)) + 1):
    print "Row: ", row, "Col: ", url_header_col
    url = wks.cell(row, url_header_col).value

    if url in blog_URLs:
        for week in range(0, get_week(sem_end_rfc3339)):
            author = blog_authors_dict[blog_IDs_dict[url]]
            try:
                comment_count = len(data[week][author])
            except KeyError:
                comment_count = 0
            wks.update_cell(row, week1_col + week, comment_count)


week_header_cell = wks.find('Week_1')
blog_URLs_list = wks.col_values(week_header_cell.col)

print "Task completed in ", (datetime.now() - script_start)
