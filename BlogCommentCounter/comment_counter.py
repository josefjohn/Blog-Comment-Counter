# Authors: Gautam Jain & Josef John

import rfc3339
from apiclient.discovery import build

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


# Returns the blog ID for the given blog URL
def get_blog_id(blog_url):
    response = blogger.blogs().getByUrl(
        url=blog_url,
        fields="id").execute()
    return response['id']


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
#list_of_blog_urls = get_blog_urls_from_file('blog_urls.txt')

#print get_all_comments(blog_id)
#print get_comments_from_blogs(list_of_blog_urls)
test_write_to_file()
#write_comments_from_blogs_to_file(list_of_blog_urls, 'blog_comments.txt')
