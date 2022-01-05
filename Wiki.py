

import wikipedia
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ObjectRepository import ObjectRepository
from mongoDBOperations import MongoDBManagement
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from transformers import BartForConditionalGeneration, BartTokenizer, BartConfig

class Wiki:

    def __init__(self, executable_path, chrome_options):
        """
        This function initializes the web browser driver
        :param executable_path: executable path of chrome driver.
        """
        try:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
        except Exception as e:
            raise Exception(f"(__init__): Something went wrong on initializing the webdriver object.\n" + str(e))

    def waitExplicitlyForCondition(self, element_to_be_found):
        """
        This function explicitly for condition to satisfy
        """
        try:
            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
            WebDriverWait(self.driver, 2, ignored_exceptions=ignored_exceptions).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, element_to_be_found)))
            return True
        except Exception as e:
            return False

    def getCurrentWindowUrl(self):
        """
        This function returns the url of current window
        """
        try:
            current_window_url = self.driver.current_url
            return current_window_url
        except Exception as e:
            raise Exception(f"(getCurrentWindowUrl) - Something went wrong on retrieving current url.\n" + str(e))

    def getLocatorsObject(self):
        """
        This function initializes the Locator object and returns the locator object
        """
        try:
            locators = ObjectRepository()
            return locators
        except Exception as e:
            raise Exception(f"(getLocatorsObject) - Could not find locators\n" + str(e))

    def findElementByXpath(self, xpath):
        """
        This function finds the web element using xpath passed
        """
        element = self.driver.find_element(By.XPATH, value=xpath)
        return element

    def findElementById(self, id):
        """
        This function finds the web element using id passed
        """
        try:
            element = self.driver.find_element(By.ID, value=id)
            return element
        except Exception as e:
            raise Exception(f"(findElementByXpath) - id provided was not found.\n" + str(e))

    def findElementByClass(self, classpath):
        """
        This function finds web element using Classpath provided
        """
        try:
            element = self.driver.find_element(By.CLASS_NAME, value=classpath)
            return element
        except Exception as e:
            # self.driver.refresh()
            raise Exception(f"(findElementByClass) - ClassPath provided was not found.\n" + str(e))

    def findElementByTag(self, tag_name):
        """
        This function finds web element using tag_name provided
        """
        try:
            element = self.driver.find_elements_by_tag_name(tag_name)
            return element
        except Exception as e:
            raise Exception(f"(findElementByTag) - ClassPath provided was not found.\n" + str(e))

    def findingElementsFromPageUsingClass(self, element_to_be_searched):
        """
        This function finds all element from the page.
        """
        try:
            result = self.driver.find_elements(By.CLASS_NAME, value=element_to_be_searched)
            return result
        except Exception as e:
            raise Exception(
                f"(findingElementsFromPageUsingClass) - Something went wrong on searching the element.\n" + str(e))

    def findingElementsFromPageUsingCSSSelector(self, element_to_be_searched):
        """
        This function finds all element from the page.
        """
        try:
            result = self.driver.find_elements(By.CSS_SELECTOR, value=element_to_be_searched)
            return result
        except Exception as e:
            raise Exception(
                f"(findingElementsFromPageUsingClass) - Something went wrong on searching the element.\n" + str(e))

    def openUrl(self, url):
        """
        This function open the particular url passed.
        :param url: URL to be opened.
        """
        try:
            if self.driver:
                self.driver.get(url)

                return True
            else:
                return False
        except Exception as e:
            raise Exception(f"(openUrl) - Something went wrong on opening the url {url}.\n" + str(e))

    def checkAmbiguity(self,searchString):

        locator = self.getLocatorsObject()
        self.openUrl("https://www.wikipedia.org/")
        search_box = self.findElementById(id=locator.getSearchBox()).send_keys(searchString,Keys.ENTER)
        #print("search box found")
        WebDriverWait(self.driver, 2)

        try:
            self.findElementByXpath(xpath=locator.getAmbigious())
            #print("Page is ambigious")
            self.closeDriver()
            return [True,self.getDisambiguatioin(searchString=searchString)]
        except NoSuchElementException as e:
            #print("Page is not ambigious")
            self.closeDriver()
            return [False]

    def fetchPageContent(self,searchString):
        #print(searchString)
        try:
            wikipage = wikipedia.page(searchString, auto_suggest=False)

            return wikipage
        except wikipedia.DisambiguationError as e:
            #raise Exception("(feedback) - Something went wrong on retrieving page contents from wiki.\n" + str(e))
            return e.options

    def fetchPageImages(self,wikipage):

        try:
            wikiimages = wikipage.images
            return wikiimages
        except Exception as e:
            raise Exception("(feedback) - Something went wrong on retrieving images from wiki.\n" + str(e))

    def fetchPageReferences(self, wikipage):

        try:
            wikiref = wikipage.references
            return wikiref
        except Exception as e:
            raise Exception("(feedback) - Something went wrong on retrieving references from wiki.\n" + str(e))


    def createsummary(self,searchString,username,password,db_name):
        try:

            page = self.fetchPageContent(searchString)
            summary = self.summarize(wiki=page.content)

            images = self.fetchPageImages(page)
            references = self.fetchPageReferences(page)

            mongoClient = MongoDBManagement(username=username, password=password)

            result = {  'summary': summary,
                        'images': images,
                        'references': references
                        }

            mongoClient.insertRecord(db_name=db_name,
                                     collection_name=searchString,
                                     record=result)
            return result
        except Exception as e:
            raise Exception("Error encountered while fetcing data from wikipedia.\n" + str(e))


    def saveDataFrameToFile(self, dataframe, file_name):
        """
        This function saves dataframe into filename given
        """
        try:
            dataframe.to_csv(file_name)
        except Exception as e:
            raise Exception(f"(saveDataFrameToFile) - Unable to save data to the file.\n" + str(e))


    def closeDriver(self):

        """
        This function is used to close the browsers opened.
        :return: Nothing
        """
        try:
            self.driver.close()
        except Exception as e:
            raise Exception(f"(closeDriver) - Error encountered while closing the data.\n" + str(e))

    def getDisambiguatioin(self,searchString):

        try:
            wikipedia.page(searchString,auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            return e.options


    def summarize(self,wiki):

        # Loading the model and tokenizer for bart-large-cnn
        tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

        inputs = tokenizer.batch_encode_plus([wiki], return_tensors='pt', truncation=True)
        summary_ids = model.generate(inputs['input_ids'], early_stopping=True)

        # Decoding and printing the summary
        bart_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return bart_summary