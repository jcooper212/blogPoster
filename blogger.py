import os
import openai
import shutil
import requests
import sys
from PIL import Image
from io import BytesIO
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPEN_AI_KEY')

from git import Repo
from pathlib import Path
from bs4 import BeautifulSoup as Soup

PATH_TO_BLOGREPO = Path('/Users/jcooper/py/genAi/jcooper212.github.io/.git')
PATH_TO_BLOG = PATH_TO_BLOGREPO.parent
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

###Load Json
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_values(json_data):
    if "title" in json_data and "tags" in json_data and "summary" in json_data:
        return {
            "title": json_data["title"],
            "tags": json_data["tags"],
            "summary": json_data["summary"]
        }
    else:
        print("Error: JSON file is missing one or more required fields.")
        return None

def update_blog(commit_msg = 'Updates blog'):
    repo = Repo(PATH_TO_BLOGREPO)
    repo.git.add(all=True)
    repo.index.commit(commit_msg)
    origin = repo.remote(name='origin')
    origin.push()

#with open(PATH_TO_BLOG/"index.html", 'w') as f:
#    f.write("WOW WOW WOW***")
#update_blog()

#use this version - will create an article and a cover image (uses story template)
def create_new_blogV2(title, content, image_url, tags):
    #new article file
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"blogPost{files+1}.html"
    
    path_to_new_content = PATH_TO_CONTENT/new_title
    path_to_template = "{}/story_template.html".format(PATH_TO_CONTENT)


    #new cover image
    img_name = f"blogImg{files+1}.png"
    save_image(image_url, file_name=f"{PATH_TO_CONTENT}/{img_name}")
    #cover_image = Path(cover_image)
    #shutil.copy(cover_image, PATH_TO_CONTENT)

    #read the template
    html_content=""
    with open(path_to_template, 'r') as file:
        html_content = file.read()
    #new_html = createBlogHtmlV2(f"content/{img_name}", title, tags, content)
    print(f">>> {title} // {tags} // {content} /////, html_content.find('ArticleTitle')")
    html_content = html_content.replace("ArticleTitle", title)
    html_content = html_content.replace("ArticleTags", tags)
    html_content = html_content.replace("ArticleContent", content)
    html_content = html_content.replace("By [Your Name], Senior Engineering Developer Consultant", " ")

    


    
    print("html_content is ", html_content)

    #write cover page
    # with open(path_to_template, 'w') as f:
    #     f.write(html_content)

    #write new blog
    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content,"w") as f:
            f.write(html_content)
            return path_to_new_content
    else:
        raise FileExistsError('file already exists')


#original DONT USE create_new_blog -- needs some love n fixin (use v2)
def create_new_blog(title, content, cover_image):
    cover_image = Path(cover_image)
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"{files+1}.html"
    path_to_new_content = PATH_TO_CONTENT/new_title

    shutil.copy(cover_image, PATH_TO_CONTENT)

    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content,"w") as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write(f"<title>{title} </title>\n")
            f.write("</head>\n")

            f.write("<body>\n")
            f.write(f"<img src='{cover_image.name}' alt='Cover Image'> <br />\n")
            f.write(f"<h1> {title} </h1>")
            #openAI --> completion engine
            f.write(content. replace("\n", "<br />\n"))
            f.write("</body>\n")
            f.write("</html>\n")
            print('blog created')
            return path_to_new_content
    else:
        raise FileExistsError('file already exists')

#Original version - not useful. Use V2
def createBlogHtml(img_name, title, tags, story_link):
    htmlStr = f"<img src='{img_name}' alt='Cover Image' class='img-fluid'>\n"
    htmlStr = htmlStr + f"<h3>{title}</h3>\n"
    htmlStr = htmlStr + f"<p style='color: grey;'>{tags}</p>\n"
    htmlStr = htmlStr + f"<a href='{story_link}' class='btn btn-primary'>Read more</a>\n"
    return htmlStr

#USE THIS Version
def createBlogHtmlV2(img_name, title, tags):
    htmlStr = f"<img src='{img_name}' alt='Cover Image' class='img-fluid'>\n"
    htmlStr = htmlStr + f"<h3>{title}</h3>\n"
    htmlStr = htmlStr + f"<p style='color: grey;'>{tags}</p>\n"
    htmlStr = htmlStr + f"<a href='{story_link}' class='btn btn-primary'>Read more</a>\n"
    return htmlStr

#DONT USE create_new_Bootsblog -- needs some love n fixin (use create_new_Blogv2)
def create_new_bootsBlog(title, content, cover_image, storyCode):
    cover_image_path = Path(cover_image)
    path_to_template = "{}/bootsBlog_template.html".format(PATH_TO_CONTENT)
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"{files+1}.html"
    path_to_new_content = PATH_TO_CONTENT/new_title

    shutil.copy(cover_image_path, PATH_TO_CONTENT)

    #read the template
    with open(path_to_template, 'r') as file:
        html_content = file.read()
    new_html = createBlogHtml(cover_image, title, "ai, microservices", "html...")
    html_content.replace(storyCode, new_html)
    print(html_content, "\n\n", new_html)

    
    print(html_content)

    #write cover page
    with open(path_to_template, 'w') as f:
        f.write(html_content)

    #write new blog
    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content,"w") as f:
            f.write(html_content)
            return path_to_new_content
    else:
        raise FileExistsError('file already exists')




def check_for_dupe_links(path_to_new_content, links):
    urls = [str(link.get("href")) for link in links] # 1.html, 2.html, 3.html...
    content_path = str(Path(*path_to_new_content.parts[-2:])) # /Users/xyz/.../1.thnml
    return content_path in urls

def write_to_index(path_to_new_content):
    with open(PATH_TO_BLOG/'index.html') as index:
        soup = Soup(index.read(), 'html.parser')
    
    links = soup.find_all('a')
    last_link = links[-1]

    if check_for_dupe_links(path_to_new_content, links):
        raise ValueError('links already exists')

    link_to_new_blog = soup.new_tag("a", href=Path(*path_to_new_content.parts[-2:]))
    link_to_new_blog.string = path_to_new_content.name.split('.')[0]
    last_link.insert_after(link_to_new_blog)

    with open(PATH_TO_BLOG/'index.html','w') as f:
        f.write(str(soup.prettify(formatter='html')))

def create_prompt(title, topic):
    if (topic == "init"):
        prompt = """
        Background:
        Rayze is a growth stage technology consulting company. We are a team of software engineers passionate in making our clients reach their ambitions.
        
        Blog
        Title: {}
        tags: python, data engineering, cloud migration, microservices, digitization, ML, AI, Large Language Models
        Summary: This Rayze blog will focus on latest trends on python, data engineering, cloud migration, microservices, digitization, ML, AI, Large Language Models. It will suggest practical solutions
        to common problems that clients encounter with these technology. It will focus on useful APIs, libraries, tools and solutions that are opensourced especially that help with cost reduction. This is a tldr punchy blog posts with helpful links
        so each blog will be 200 to 500 words in length.
        Full Text:""".format(title)
    else:
        prompt = """
        Background:
        A useful technical blog on the latest APIs, libraries, tools, trends in {}      
        Blog
        Title: {}
        tags: {}
        Summary: Write a technical engineering blog on {}. IIt will focus on latest trends, and suggest practical solutions
        to common problems that clients encounter with this technology. It will focus on useful APIs, libraries, tools and solutions that are opensourced especially that help with cost reduction. This is a tldr punchy blog posts with helpful links
        so each blog will be 200 to 500 words in length.
        Full Text:""".format(topic, title, topic, topic)
    return prompt


def dalle2_prompt(title):
    prompt = f"Space exploration with {title}"
    return prompt

def save_image(image_url, file_name):
    image_res = requests.get(image_url, stream = True)

    if image_res.status_code == 200:
        original_image = Image.open(BytesIO(image_res.content))
        header_banner_size = (300, 300)  # Adjust the width and height as needed
        resized_image = original_image.resize(header_banner_size)
        resized_image.save(file_name)  # Replace with the desired path and filename
        # with open(file_name, 'wb') as f:
        #     shutil.copyfileobj(image_res.raw, f)
    else:
        print('err img downloading')
    return image_res.status_code

######### MAIN
#print(create_prompt(title))
#write_to_index(path_to_new_content)
#update_blog()


#Gen Blog
if len(sys.argv) != 2:
    print("Usage: python3 blogger.py <json_file>  {|} you passed in: ", sys.argv)
    sys.exit(1)

# Read json input
json_data = read_json_file(sys.argv[1])
print(json_data)
prompt_str = ""
if "title" in json_data and "tags" in json_data and "heading" in json_data:
    prompt_str = f"{json_data['heading']} "
    prompt_str = prompt_str + f"Title: {json_data['title']}  "
    prompt_str = prompt_str + f"Tags: {json_data['tags']}  "
else:
    print("Error: JSON file is missing one or more required fields.")
    
#Gen OpenAI copmpletion response
response = openai.Completion.create(
    #model = "text-davinci-003",
    model = "gpt-3.5-turbo-instruct",
    prompt = prompt_str,
    temperature = 0.7,
    max_tokens = 1000)

blog_content = response['choices'][0]['text']
print(blog_content)

#Gen Image
image_prompt = dalle2_prompt(json_data['title'])
response = openai.Image.create(prompt=image_prompt,
n=1, size="256x256")
image_url = response['data'][0]['url']
print(image_url)

path_to_new_content = create_new_blogV2(json_data['title'], blog_content, image_url, json_data['tags'])
#write_to_index(path_to_new_content)
update_blog()
    
