
import wikipedia

from mongoDBOperations import MongoDBManagement


class Wiki:

    def __init__(self):
        """
        This function initializes the web browser driver

        """

    def fetchPageContent(self,searchString):
        try:
            wikipage = wikipedia.page(searchString)
            return wikipage
        except Exception as e:
            raise Exception("(feedback) - Something went wrong on retrieving page contents from wiki.\n" + str(e))

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
            images = self.fetchPageImages(page)
            references = self.fetchPageReferences(page)

            mongoClient = MongoDBManagement(username=username, password=password)

            result = {  'summary': page.summary,
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