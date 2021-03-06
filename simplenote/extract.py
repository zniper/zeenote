import requests
import logging
import json


from simplenote.settings import ALCHEMY_API_KEY, ALCHEMY_API_URL
from simplenote.settings import DIFFBOT_API_URL

logging.basicConfig()
logger = logging.getLogger(__name__)

class Extracter:
    _url = ''
    _text = ''

    def __init__(self, url):
        self._url = url
        self.extractText()
    
    def getText(self):
        return self._text

    def extractText(self):
        pass


class AlchemyExtracter(Extracter):
    
    def extractText(self):
        """ Call API function from AlchemyAPI to extract text
        """
        params = {}
        params['url'] = self._url
        params['apikey'] = ALCHEMY_API_KEY
        params['outputMode'] = 'json'
        print params
        try:
            
            r = requests.get(ALCHEMY_API_URL+'URLGetText', auth=('user', 'pass'))
            print r.json
            if r.json['status'] == 'OK':
                self._text = r.json['text']
        except:
            logger.error('Error when calling AlchemyAPI')
            raise
            

class DiffBotExtracter(Extracter):
    
    def extractText(self):
        """ Call API function from AlchemyAPI to extract text
        """
        params = {}
        try:
            print self.url
            r = requests.get(DIFFBOT_API_URL + source, params=params)
            print r.status_code
            if r.status_code == 200:
                self._text = r.json['text']
        except:
            logger.error('Error when working with DiffBot')
            raise
def ExtractText(source):
    params = {}
    try:
        r = requests.get(DIFFBOT_API_URL + source, params=params)
        data =  r.json()
        if r.status_code == 200:
            return data['text']
    except:
        logger.error('Error when working with DiffBot')
        raise
