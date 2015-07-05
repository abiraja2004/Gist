import webapp2
import logging

import base
import ajax
import tasks
import userinput
import urllib

class FrontHandler(base.Handler):
    def get(self):
        self.render("gist.html")
   
    def post(self):
        request_data = urllib.unquote(self.request.body)
        user_input = request_data[7:]

        try:
            response = userinput.handle_user_search(user_input)
            self.render('gist.html', key_points=response.key_points, product_name = response.product_name)
        except Exception, e:
            logging.info(e)
            self.render('gist.html', exception = str(e))
            
#this maps urls to actual website code   
app = webapp2.WSGIApplication([
    ('/?', FrontHandler), ('/ajax/getkeypoints/?', ajax.GetKeyPointsHandler),
    ('/tasks/updatekeypointdatabase/?', tasks.UpdateKeypointsHandler),
    ('/wait/?', ajax.WaitHandler),
], debug=True)
