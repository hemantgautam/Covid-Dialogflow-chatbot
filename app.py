from flask import Flask, request, make_response
import json
import os
from flask_cors import cross_origin
from SendEmail.sendEmail import EmailSender
from logger import logger
from mongo import mongo_connection
from covid import covidApp

app = Flask(__name__)

# webhook root with method post
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    '''
        Dialog flow is sending request in json format.
        getting the json.
    '''
    req = request.get_json(silent=True, force=True)

    # Sending json in a function to extract its parameters
    res = processRequest(req)

    # dumping the response in json to send back to dialog flow
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    log = logger.Log()
    result = req.get("queryResult")
    intent = result.get("intent").get('displayName')
    parameters = result.get("parameters")
    fulfillmentText = ''

    # Validating the intent name to perform specific task
    if (intent == 'Covid19_Intent'):

        # storing all the required params in variable to use accodingly
        sessionID = req.get('responseId')
        user_says = result.get("queryText") 
        user_email = parameters.get("user_email")
        user_pincode = parameters.get("user_pincode")
        user_name = parameters.get("user_name")
        user_mobile = parameters.get("user_mobile")

        '''
            direct json of parameters is used to store it in Mongo DB,
            as mongo db take values in dict format
        '''
        user_details = parameters

        # Mongo DB connection initialization
        db_connect = mongo_connection.DatabaseConnect()

        # Email sender class initialization
        email_sender = EmailSender()

        # add_user_data Method call to store data in DB
        db_connect.add_user_data(sessionID, user_details)

        # send_covid_data method call to send email to users email id
        email_sender.send_covid_data(user_email)

        fulfillmentText = "Thanks. We have sent necessary details in your email.\n\nEnter 'Y' to see worldwide covid cases or Enter 'Country Name or Country Code or State Code'.\n\nTo see demographically covid cases open this link https://covid19-flask-lui.herokuapp.com/demographic-covid-data"
        log.write_log(sessionID, "Bot Says: "+fulfillmentText)

        # Custom fulfillment text is sending back to dialogflow
        return {"fulfillmentText": fulfillmentText}

    # Validating the intent name to perform specific task
    elif (intent == 'GetCovidData'):

        '''
            Once user's info is captured, user type any country name,
            country code, state code to get the latest Covid cases,
            country_code_state_name variable store the same user input.
        '''
        country_code_state_name = parameters.get("country_code_state_name")

        # class CovidInformation initialization
        covid_info = covidApp.CovidInformation()

        '''
            we are asking user to enter 'Y' to get world wide data and
            in code we are processing it and calling worldwide covid data
        '''
        if country_code_state_name.upper() == "Y":

            # get_world_covid_data method call for worldwide covid data
            covid_world_data = covid_info.get_world_covid_data()

            # Custom fulfillment text sends back world covid cases to dialogflow
            return {"fulfillmentText": covid_world_data}
        else:
            try:

                '''
                    If user enter country code,state name or country name,
                    this is code gets excuted and returns back with specific data
                '''
                covid_data_by_code_name = covid_info.get_covid_data_by_country(
                    country_code_state_name)

                # Custom fulfillment text sends back specific country/state covid cases to dialogflow
                return {"fulfillmentText": covid_data_by_code_name}
            except:

                # If no match found, it returns differnt message
                return {"fulfillmentText": "Couldn't find the match.\n\nEnter 'Y' to see worldwide covid cases or Enter 'Country Name or Country Code or State Code'.\n\nTo see demographically covid cases open this link https://covid19-flask-lui.herokuapp.com/demographic-covid-data"}

    else:
        log.write_log(sessionID, "Bot Says: " + result.fulfillmentText)


if __name__ == '__main__':
    app.run()
