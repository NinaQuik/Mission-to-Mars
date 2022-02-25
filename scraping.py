


# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

# Import pandas and datetime
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    
    #run all the scraping functions and store the results to a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_urls": hemisphere_info(browser)
    }
    #stop the webdriver and return the data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #set up html parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #add error handling 
    try:
        slide_elem = news_soup.select_one('div.list_text')


        #Find title of first article
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        news_summary = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_summary


# ### Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #Assign columns and set index of dataFrame
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    #drop unnessary and redundant row
    df = df.drop(df.index[0])

    #Convert dataFrame to HTML
    return df.to_html(classes='table table-striped')

def hemisphere_info(browser):
    #visit url
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    #set up html parser
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    results = hemi_soup.find_all('div', class_='item')

    #create an empty list to hold urls and image titles
    hemisphere_image_urls = []

    #Get the titles for the four images
    try:
        for result in results:
            #create a dictionary to hold the title and url
            image_dic = {}
            # retrieve the  title
            image_dic["title"] = result.find('h3').get_text()
            hemisphere_image_urls.append(image_dic)
    except AttributeError as e:
            print(e)

    # Now get the full resolution image urls for each hemisphere
    try:
        for x in range(4):
            #click on url to open up planet specific page
            browser.links.find_by_partial_text('Enhanced')[x].click()
            #add the new page to beautiful soup
            planet_details = browser.html
            details_soup = soup(planet_details, 'html.parser')
            #grab the url for the full size image
            full_url_rel = details_soup.find('a', text = 'Sample').get('href')
            # add the url to the list of dictionaries
            hemisphere_image_urls[x]['img_url'] = f'https://marshemispheres.com/{full_url_rel}'
            browser.back()
    except AttributeError as e:
            print(e)
    return hemisphere_image_urls








