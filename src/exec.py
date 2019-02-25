from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import urllib.parse
import time
import sys
import re
from selenium.common.exceptions import NoSuchElementException

###
# Set for each environment
###
DRIVER_PATH = "C:/Drivers/chromedriver_win32/chromedriver.exe" #Webdriver
WAIT_LIMIT = 20 #Wait limit
PAGING_WAIT_SEC = 1 #Paging wait time

###
# Instagram Web Page Settings
###
#URL
loginURL = "https://www.instagram.com/accounts/login/?source=auth_switcher" #URL
tagSearchURL = "https://www.instagram.com/explore/tags/{}/?hl=ja" #Search URL

#selectors
labelsXpath = '//label'
myPageXpath = '//span[contains(@class,\'glyphsSpriteUser__outline\')]'
firstArticleXpath = '//article/div[1]/div[1]/div[1]/div[1]/div[1]/a'
likeButtonSelector = 'button.coreSpriteHeartOpen'
likeXpath = '//button/span[contains(@class,\'glyphsSpriteHeart__outline\')]'
likedXpath = '//button/span[contains(@class,\'glyphsSpriteHeart__filled\')]'
nextPagerSelector = 'a.coreSpriteRightPaginationArrow'

#counter
likedCounter = 0

##
# Processing part
##
class CompareUrl:
    """
    WebDriverWait custom condition.
    Check NextButton's href attr is changed
    If checkUrl equal NextButton's href, return false
    """
    def __init__(self,locator, checkUrl):
        self.locator = locator
        self.checkUrl = checkUrl

    def __call__(self, driver):
        nextButton = driver.find_element(*self.locator)
        if self.checkUrl != nextButton.get_attribute("href"):
            return nextButton
        else:
            return False

def instagramLike(username,password,tagName):
    """
    Like all searched images
    Parameters
    ----------
    username : String
        Login user id
    password : String
        Login password
    tagName
        Search tagName. # is not required
        ex) "hoge"
    """
    #Execute browser
    browser = webdriver.Chrome(executable_path=DRIVER_PATH)

    #Login 
    browser.get(loginURL)
    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "footer"))
    )
    labelsField = browser.find_elements_by_xpath(labelsXpath)
    usernameField = browser.find_element_by_xpath("//*[@id=\"" + labelsField[0].get_attribute("for") + "\"]")
    usernameField.send_keys(username)
    passwordField = browser.find_element_by_xpath("//*[@id=\"" + labelsField[1].get_attribute("for") + "\"]")
    passwordField.send_keys(password)
    passwordField.send_keys(Keys.RETURN)
    #Finished login.
    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.XPATH, myPageXpath))
    )
    encodedTag = urllib.parse.quote(tagName)
    encodedURL = tagSearchURL.format(encodedTag)
    print("encodedURL:{}".format(encodedURL))
    browser.get(encodedURL)
    #Finished tag search.
    WebDriverWait(browser, 10).until(
        expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "article"))
    )
    #Get and click first article.
    firstArticle = browser.find_elements_by_xpath(firstArticleXpath)
    firstArticle[0].click()

    #Loop while next button exist
    likedCounter = 0
    while True:
        browser.implicitly_wait(PAGING_WAIT_SEC)
        try:
            try:
                #Wait display like button.
                WebDriverWait(browser, WAIT_LIMIT).until(
                    expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, likeButtonSelector))
                )
                browser.find_element_by_xpath(likeXpath).text
                browser.find_element_by_css_selector(likeButtonSelector).click()

                #Wait like status changed.
                WebDriverWait(browser, WAIT_LIMIT).until(
                    expected_conditions.presence_of_all_elements_located((By.XPATH, likedXpath))
                )
                browser.quit()
                exit()
                likedCounter += 1
                print("liked {} ".format(likedCounter))
            except NoSuchElementException as e1:
                print(e1)
                print("already liked article")

            nextUrl = browser.find_element_by_css_selector(nextPagerSelector).get_attribute("href")
            browser.find_element_by_css_selector(nextPagerSelector).click()

            #Wait display next article.
            WebDriverWait(browser, WAIT_LIMIT).until(CompareUrl((By.CSS_SELECTOR,nextPagerSelector),nextUrl))
        except Exception as e2:
            print(e2)
            break #もう次へボタンが存在しない場合、エラーをはくのでそこで終了

    print("You liked {} media".format(likedCounter))



###
# execute
###
if __name__ == '__main__':
    args = sys.argv
    if(4 == len(args)):
        instagramLike(args[1],args[2],args[3])
    else:
        
        print("パラメータが不正です。")
        print("引数1:ユーザー名")
        print("引数2:パスワード")
        print("引数3:検索するタグ")