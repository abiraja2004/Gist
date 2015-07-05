import json
import logging
import urllib
import urlparse
import time
import copy

import base
import userinput
import getreview

class GetKeyPointsHandler(base.Handler):
    def post(self):
        # get info from ajax request
        # load the data as json (javascript ajax should sent data as json)
        # proccess it as neccessary
        request_data = json.loads(self.request.body)

        url = request_data['userInput']

        # create response for client
        # including any neccesary data
        response = {'url': url}
        try:
            review = userinput.handle_user_search(url)
            response['key_points'] = review.key_points
            response['product_name'] = review.product_name
        except Exception, e:
            logging.info(e)
            response['exception'] = str(e)
        finally:
            # write response back to client
            # response is json
            self.response.out.write(json.dumps(response))

class WaitHandler(base.Handler):
    def post(self):
        # get and process url
        logging.info(self.request.body)
        request_data = json.loads(self.request.body)
        user_input = request_data['userInput']

        # send request
        response = {'url': user_input}
        try:
            review = userinput.handle_user_search(user_input)
            
            if review is None:
                raise userinput.NotInDatabaseException('URL not in database. Please wait.')

            response['key_points'] = review.key_points
            response['product_name'] = review.product_name
        except Exception, e:
            # error
            logging.info(e)
            response['exception'] = str(e)
        finally:
            # write response to client
            logging.info(response)
            self.response.out.write(json.dumps(response))