import os
import time
import queue
import requests

from threading import Thread

from modules import milanuncios

# Observer
class Observer(Thread):
    def __init__(self, q: queue, *args, **kwargs):
        self.queue = q
        super().__init__(*args, **kwargs)
        self.daemon = True

    def run(self):
        while True:
            self.milanuncios()
            time.sleep(5)
            
    def milanuncios(self):
        url = 'https://www.milanuncios.com/ofertas-de-empleo-en-'+\
            'cantabria/?demanda=n&orden=relevance&fromSearch=1'
        scraper = milanuncios.Scraper(url, 2, {})
        scraper.set_all()
        scraper.filter_all()
        scraper.to_csv('milanuncios.csv')
        
def main():
    # Observer
    q = queue.Queue()
    obs = Observer(q)
    obs.start()
    obs.join()

if __name__ == '__main__':
    main()