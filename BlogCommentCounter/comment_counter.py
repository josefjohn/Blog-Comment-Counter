# Authors: Gautam Jain & Josef John

import pprint
import gspread
import rfc3339
from apiclient.discovery import build
from urlparse import urlparse

#######################################################
## TO BE EDITED
start_of_week = [1359417600, 1360022400, 1360627200, 1361232000, 1361836800,
                 1362441600, 1363046400, 1363651200, 1364256000, 1364860800,
                 1365465600, 1366070400, 1366675200, 1367280000, 1367884800,
                 1368489600, 1369174400]
#######################################################

# Google Docs Worksheet Info
wks_name = 'Test Spreadsheet'

# Semester dates
sem_start = '2013-01-21'  # Must be a Monday
sem_end = '2013-05-05'    # Must be a Sunday

sem_start = rfc3339.strtotimestamp(sem_start + 'T00:00:00-08:00')
sem_end = rfc3339.strtotimestamp(sem_end + 'T23:59:59-07:00')

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
    #return url.find('blogspot.com') != -1
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
    # Request a list of posts between specified dates. Only return post IDs.
    response = blogger.posts().list(
        blogId=blog_id,
        startDate=sem_start_rfc3339,
        endDate=sem_end_rfc3339,
        fields='items/id').execute()

    # Reformat response into a list
    post_ids = []
    for post in response.get('items', []):
        post_ids.append(str(post['id']))
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
        comments.append({
            'author_id': str(comment['author']['id']),
            'author_name': str(comment['author']['displayName']),
            'comment_id': str(comment['id']),
            'publish_date': str(comment['published'])})

    return comments


# Returns a list of all comments for the give blog that
# were published between sem_start and sem_end
def get_all_comments(blog_id):
    posts = get_posts(blog_id)
    comments = []

    for post in posts:
        comments += get_comments(blog_id, post)

    return comments


#returns list of dictionaries
#each dictionary maps to a week
#each dictionary contains author_id keys mapping to a set of comment_ids for that week
#for each dictionary, keys are author_id, values are sets of the comments
#call len(dict[author_id]) to get comments for a given week
def get_total_comments(blog_ids):
    # Initialize dictionaries
    total_comments_dictionary_for_week = []
    for i in range(0, len(start_of_week) - 1):
        total_comments_dictionary_for_week.append(dict())

    # Iterate through all blogs
    for blog_id in blog_ids:
        post_ids = get_posts(blog_id)

        # Iterate through every post
        for post_id in post_ids:
            list_of_comments_dict = get_comments(blog_id, post_id)

            # Iterate through every comment
            for comment in list_of_comments_dict:
                author_id = comment['author_id']
                comment_id = comment['comment_id']
                publish_date = comment['publish_date']

                week = get_week_from_publish_date(publish_date)
                if week < 0 or week > 16:
                    print "error"
                    # Change this
                    return
                week_comments_dict = total_comments_dictionary_for_week[week]

                pprint.pprint(week_comments_dict)

                if author_id in week_comments_dict.keys():
                    pprint.pprint(week_comments_dict[author_id])
                    week_comments_dict[author_id] = week_comments_dict[author_id].add(comment_id)
                else:
                    # set with comment_ids
                    set_of_comment_ids = set()
                    set_of_comment_ids.add(comment_id)
                    week_comments_dict[author_id] = set_of_comment_ids

    return total_comments_dictionary_for_week

          
def get_week_from_publish_date(publish_date):
    date_in_long = rfc3339.strtotimestamp(publish_date)
    for i in range(0, len(start_of_week) - 1):
        if date_in_long > start_of_week[i] and date_in_long < start_of_week[i + 1]:
            print "week ", i
            return i
    return -1

#####################################################################
#for each url, get all comments
def get_comments_from_blogs(list_of_blog_urls):
    all_comments_dict = {}
    for blog_url in list_of_blog_urls:
        blog_id = get_blog_id(blog_url)
        list_of_comments = get_all_comments(blog_id)
        all_comments_dict[blog_id] = list_of_comments
    return all_comments_dict

#cant do this, can only write string not lists
#def write_comments_from_blogs_to_file(list_of_blog_urls, file):
#    file_to_write_to = open(file, 'w')
#    for blog_url in list_of_blog_urls:
#        blog_id = get_blog_id(blog_url)
#        list_of_comments = get_all_comments(blog_id)
#        file_to_write_to.write(list_of_comments+'\n')
#    file_to_write_to.close()


#writes to file, 'a' appends, 'w' just writes
def test_write_to_file():
    with open('test.txt', 'a') as file_to_write_to:
        file_to_write_to.write('test\n')

        
#gets the blog_urls from the file given
def get_blog_urls_from_file(file):
    blog_urls = [blog_url.strip() for blog_url in open(file)]
    return blog_urls

#################################################

blog_URLs = get_blog_URLs()

blog_IDs_dict = {}
blog_authors_dict = {}

for blog_URL in blog_URLs:
    blog_ID = get_blog_id(blog_URL)
    blog_IDs_dict[blog_URL] = blog_ID

pprint.pprint(blog_IDs_dict)

print '################################'
print '################################'
print '################################'
print get_total_comments(blog_IDs_dict.itervalues())
