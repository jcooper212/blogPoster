import os
import openai
import shutil
import requests
import sys
from PIL import Image
from io import BytesIO
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

def update_blog(commit_msg = 'Updates blog'):
    repo = Repo(PATH_TO_BLOGREPO)
    repo.git.add(all=True)
    repo.index.commit(commit_msg)
    origin = repo.remote(name='origin')
    origin.push()

#with open(PATH_TO_BLOG/"index.html", 'w') as f:
#    f.write("WOW WOW WOW***")
#update_blog()

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

def createBlogHtml(img_name, title, tags, story_link):
    htmlStr = f"<img src='{img_name}' alt='Cover Image' class='img-fluid'>\n"
    htmlStr = htmlStr + f"<h2>{title}</h2>\n"
    htmlStr = htmlStr + f"<p>{tags}</p>\n"
    htmlStr = htmlStr + f"<a href='{story_link}' class='btn btn-primary'>Read more</a>\n"
    return htmlStr

def create_new_bootsBlog(title, content, cover_image, storyCode):
    cover_image = Path(cover_image)
    path_to_template = "{}/bootsBlog_template.html".format(PATH_TO_CONTENT)
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"{files+1}.html"
    path_to_new_content = PATH_TO_CONTENT/new_title

    shutil.copy(cover_image, PATH_TO_CONTENT)

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
    prompt = f"Abstract anime image of {title}"
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
    print("Usage: python blogger.py <topic> <|> you passed in: ", sys.argv)
    sys.exit(1)

# Access the command-line arguments
topic = sys.argv[1]
if topic == "init":
    title = "Rayze Daily Peek - Technology Strategy, Engineering and AI"
else:
    title = "Practical Engineering with {}".format(topic)
response = openai.Completion.create(
    model = "text-davinci-003",
    prompt = create_prompt(title, topic),
    temperature = 0.7,
    max_tokens = 1000)

blog_content = response['choices'][0]['text']
print(blog_content)

#Gen Image
image_prompt = dalle2_prompt(title)
response = openai.Image.create(prompt=image_prompt,
n=1, size="256x256")
image_url = response['data'][0]['url']
print(image_url)

##Create Blog and update web page
#path_to_new_content = create_new_blog(title, blog_content, 'titlex.png')
save_image(image_url, file_name=f"BLOGPOST1.png")
path_to_new_content = create_new_bootsBlog(title, blog_content, 'BLOGPOST1.png', 'BLOGPOST1')
write_to_index(path_to_new_content)
update_blog()
    


####### HTML TEMPLATE
                    # <img src="https://via.placeholder.com/300" alt="Blog Post Image" class="img-fluid">
                    # <h2>Blog Post Title 1</h2>
                    # <p>This is a sample blog post. It could contain some interesting content about a specific topic.
                    # </p>
                    # <a href="#" class="btn btn-primary">Read more</a>
