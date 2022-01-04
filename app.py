from flask import Flask, render_template, request, jsonify, Response, url_for, redirect
import pandas as pd
from Wiki import Wiki
from logger_class import getLog
from mongoDBOperations import MongoDBManagement

db_name = 'wiki_summarization'
username='dipak67000'
password='Joblogin1'

logger = getLog('Wikipedia.py')

app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
            searchString = request.form['content']
            print(searchString)
            summary_obj = Wiki()
            mongoClient = MongoDBManagement(username=username, password=password)
            if mongoClient.isCollectionPresent(collection_name=searchString, db_name=db_name):
                response = mongoClient.findAllRecords(db_name=db_name, collection_name=searchString)
                print("fetching from the database")
                reviews = [i for i in response]
                result = reviews[0]
                summary_obj.saveDataFrameToFile(file_name="static/summary_data.csv",
                                                    dataframe=pd.DataFrame.from_dict(result, orient='index').transpose())

                print(result)
                return render_template('results.html', result=result)  # show the results to user
            else:
                print('fetching from wikipedia')
                result = summary_obj.createsummary(searchString=searchString, username=username, password=password, db_name = db_name)
                summary_obj.saveDataFrameToFile(file_name="static/summary_data.csv",
                                                dataframe=pd.DataFrame.from_dict(result, orient='index').transpose())
                return render_template('results.html', result=result)
    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.run()  # running the app on the local machine