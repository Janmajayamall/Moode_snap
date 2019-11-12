from selenium import webdriver
import requests
import json
import time

class ScrapeMoodleResources():

    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.username = ''
        self.password = ''
        self.session = requests.session()
        self.currentDir = '/Users/janmajayamall/desktop/test1'
    

    def get_download_links(self):
        raw_links = [link_f.get_attribute('href') for link_f in self.driver.find_elements_by_tag_name('a')]

        links_resources = list(filter( lambda _link_val: _link_val.find('resource') > -1, raw_links))
        links_plugins = list(filter( lambda _link_val: _link_val.find('/pluginfile.php') > -1, raw_links))
        links_folders = list(filter( lambda _link_val: _link_val.find('/folder') > -1, raw_links))

        links_plugins=map(lambda _link: _link+'/?forcedownload=1', links_plugins)
        
        return links_resources, links_plugins, links_folders

    def download_url(self, _link):
        response = self.session.get(_link)
        filename = response.headers['Content-Disposition'].split(';')[1].split('=')[1][1:-1]
        #writing to the file
        with open(self.currentDir+'/'+filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
            
    def download_course_files(self):
        links_resources, links_plugins, links_folders = self.get_download_links()
        
        #downloading resource files
        for _link in links_resources:
            self.download_url(_link)
            time.sleep(5)
        for _link in links_plugins:
            self.download_url(_link)
            time.sleep(5)
        #if folders exist


    
    def get_courses_links(self):
        links_courses = [link_c.get_attribute('href') for link_c in self.driver.find_elements_by_css_selector('.btn-primary')]
        return links_courses

    def set_cookies_session(self):
        self.session.cookies.update({cookie['name']:cookie['value'] for cookie in self.driver.get_cookies()})

    def login_moodle(self):
        self.driver.get('https://hkuportal.hku.hk/cas/login?service=https%3A%2F%2Fmoodle.hku.hk%2Flogin%2Findex.php%3FauthCAS%3DCAS')
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')

        with open('config.json') as file:
            data = json.load(file)
            self.username = data['username']
            self.password = data['password']

        username.send_keys(self.username)
        password.send_keys(self.password)
        self.driver.find_element_by_class_name('image').click()
    
    def snap_moodle(self):

        #getting course links 
        links_courses = self.get_courses_links()

        #setting up request session
        self.set_cookies_session()

        #navigating through each course and downloading the resources       REMEMBER TO ADD THE FEATURE OF CREATING NEW DIRECTORY FOR EACH COURSE
        for course_link in links_courses:
            self.driver.get(course_link)
            self.download_course_files()



moodle_srcape = ScrapeMoodleResources()
moodle_srcape.login_moodle()
moodle_srcape.snap_moodle()

