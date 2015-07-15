#!/bin/python

# -*- coding: utf-8 -*-

import MySQLdb

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf, InterpType

import urllib
import os
import shutil
import datetime
import json

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.crawler import CrawlerProcess
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from Wallhaven.spiders.wallhaven import WallhavenSpider

##### CONSTANTS AND VARIABLES #####

PATH_TEMP_DIR = '/tmp/wallhaven'
PATH_IMAGES_DIR = os.path.join(os.path.expanduser('~'),'Wallhaven Gallery')
PATH_QUERY_RESULTS = os.path.join(os.path.join(os.getcwd(), 'resources'), 'query_results.json')
FILE_GUI = 'gui_wallhaven.glade'

print PATH_IMAGES_DIR
print PATH_QUERY_RESULTS
print

images_list = []
images_counter = 0
image_index = 0

class Image:
    def __init__(self, name, width, height, format, url, query):
        self.name = name
        self.width = width
        self.height = height
        self.format = format
        self.url = url
        self.query = query
    
    def get_name(self):
        return self.name
    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_format(self):
        return self.format
    
    def get_url(self):
        return self.url
    
    def get_query(self):
        return self.query

class Wallhaven_Crawler:
    def __init__(self, query):
        self.query = query
        
        # Creation of spider from query
        self.spider = WallhavenSpider(self.query)
        
        # Getting scrapy project settings
        self.settings = get_project_settings()
        
        # Creation of crawler from spider and scrapy project settings
        self.crawler = Crawler(self.settings)
        self.crawler.signals.connect(reactor.stop, signal = signals.spider_closed)
        self.crawler.configure()
        
    def start(self):
        # Crawling from spider
        self.crawler.crawl(self.spider)
        self.crawler.start()
        
        # Logging all process
        #log.start()
        #log.msg('Reactor activated.')
        # Execution of twisted reactor
        reactor.run() # The script will block here until the 'spider_closed' signal is sent
        #log.msg('Reactor stopped.')

class Wallhaven_BD():
    server_name = 'localhost'
    user_name = 'wallhaven_user'
    password = 'wallhaven'
    database_name = 'WallhavenGallery'
    table_name = 'Image'
    
    def __init__(self):
        self.connection = MySQLdb.connect(host = self.server_name, user = self.user_name, passwd = self.password, db = self.database_name)
        self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if not self.table_exists():
            self.create_database_table()
        
    def table_exists(self):
        self.cursor.execute("SHOW TABLES LIKE '" + self.table_name + "'")
        
        return (self.cursor.rowcount > 0)
        
    def create_database_table(self):
        query = "CREATE TABLE " + self.table_name
        query += "(Name VARCHAR(50) PRIMARY KEY, Width INT, Height INT,"
        query += "Format VARCHAR(10), Url VARCHAR(150), Query VARCHAR(500), Local_path VARCHAR(1000))"
        self.cursor.execute(query)
        
        self.connection.commit()
        
    def insert_image(self, name, width, height, format, url, query, local_path):
        consulta = "INSERT INTO " + self.table_name + " VALUES('" + name + "', " + str(width) + ", "
        consulta += str(height) + ", '" + format + "', '" + url + "', '" + query + "', '" + local_path + "')"
        self.cursor.execute(consulta)
        
        self.connection.commit()
        
        if self.cursor.rowcount == 1:
            success = True
        else:
            success = False
        
        return success
        
    def select_image(self, name):
        self.cursor.execute("SELECT * FROM " + self.table_name + " WHERE Name = '" + name + "'")
        
        return self.cursor.fetchone()
    
    def select_all_images(self):
        self.cursor.execute("SELECT * FROM " + self.table_name)
        
        return self.cursor.fetchall()
        
    def close_connection(self):
        self.cursor.close()
        self.connection.close()

class Wallhaven_GUI:
    def __init__(self):
        # Temporal local storage link
        self.create_temporal_directory()
        
        # Data model link
        self.database_table = Wallhaven_BD()
        
        # Interface link
        self.builder = Gtk.Builder()
        self.builder.add_from_file(FILE_GUI)
        self.handlers = { "onExit": self.on_exit,
                        "onSearch": self.on_search,
                        "onNextImage": self.on_next_image,
                        "onPreviousImage": self.on_previous_image,
                        "onSaveImage": self.on_save_image
                        }
        
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("mainWindow")
        self.window.show_all()
    
    def on_search(self, button):
        global images_list
        global images_counter
        global image_index
        
        searchQueryEntry = self.builder.get_object("searchQueryEntry")
        query = searchQueryEntry.get_text()
        
        if not query: # If query is empty
            query = 'example image'
        
        self.start_crawler(query)
        self.clean_query_results()
        self.read_query_results()
        
        if images_counter > 0:
            # Results were found
            self.load_images_counter(query)
            self.load_image(image_index + 1, images_list[image_index])
            
            button = self.builder.get_object("previousButton")
            button.set_sensitive(False)
            
            if images_counter == 1:
                button = self.builder.get_object("nextButton")
                button.set_sensitive(False)
            
            mainPanel = self.builder.get_object("mainPanelBox")
            mainPanel.remove(self.builder.get_object("searchPanel"))
            mainPanel.add(self.builder.get_object("resultsPanel"))
        else:
            # Results were not found
            text = self.builder.get_object("noResultsText")
            text.set_text('0 results from query "' + query + '"')
            mainPanel = self.builder.get_object("mainPanelBox")
            mainPanel.remove(self.builder.get_object("searchPanel"))
            mainPanel.add(self.builder.get_object("noResultsPanel"))
        
    def on_next_image(self, button):
        global images_list
        global image_index
        
        image_index += 1
        self.load_image(image_index + 1, images_list[image_index])
        
        button = self.builder.get_object("previousButton")
        button.set_sensitive(True)
        if image_index == (images_counter - 1):
            button = self.builder.get_object("nextButton")
            button.set_sensitive(False)
        
    def on_previous_image(self, button):
        global images_list
        global image_index
        
        image_index -= 1
        self.load_image(image_index + 1, images_list[image_index])
        
        button = self.builder.get_object("nextButton")
        button.set_sensitive(True)
        if image_index == 0:
            button = self.builder.get_object("previousButton")
            button.set_sensitive(False)
        
    def on_save_image(self, button):
        global images_list
        global image_index
        
        image = images_list[image_index]
        url = image.get_url()
        local_temp_path = os.path.join(self.local_path_dir, url.split('/')[-1])
        local_path_image = os.path.join(PATH_IMAGES_DIR, image.get_name() + '.' + image.get_format())
        
        # Creation of images directory if not exists
        if not self.exists_images_directory():
            self.create_images_directory()
        
        # Move of image from temporal directory to images directory
        os.rename(local_temp_path, local_path_image)
        print "Info: Moved '" + local_temp_path + "' to '" + local_path_image + "'"
        
        # Insertion in database table
        self.database_table.insert_image(
            image.get_name(),
            image.get_width(),
            image.get_height(),
            image.get_format(),
            url,
            image.get_query(),
            local_path_image
            )
    
    def on_exit(self, window):
        # Removal of temporary directory and its content
        shutil.rmtree(self.local_path_dir)
        print "Info: Removed temporary directory '" + self.local_path_dir + "'"
        
        Gtk.main_quit()
    
    def create_temporal_directory(self):
        self.local_path_dir = PATH_TEMP_DIR + datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")
        try:
            os.mkdir(self.local_path_dir)
            print "Info: Created temporary directory '" + self.local_path_dir + "'"
        except:
            sys.exit("Error: Directory '" + self.local_path_dir + "' could not be created")
    
    def start_crawler(self, query):
        crawler = Wallhaven_Crawler(query)
        crawler.start()
    
    def clean_query_results(self):
        images_list = []
        images_counter = 0
        image_index = 0
    
    def read_query_results(self):
        global images_list
        global images_counter
        
        results_file = open(PATH_QUERY_RESULTS, 'r')
        for json_line in results_file.readlines():
            object = json.loads(json_line)
            image = Image(object["name"], object["width"], object["height"], object["format"], object["url"], object["query"])
            images_list.append(image)
        results_file.close()
        
        images_counter = len(images_list)
        
        #print image.get_name()
        #print image.get_width()
        #print image.get_height()
        #print image.get_format()
        #print image.get_url()
        #print image.get_query()
        #print
    
    def load_images_counter(self, query):
        resultsLabel = self.builder.get_object("imageResultsCounterLabel")
        resultsLabel.set_text(str(images_counter) + ' results from query "' + query + '"')
    
    def load_image(self, image_index, image):
        url = image.get_url()
        
        image_local_path = self.download_image(url)
        self.resize_and_set_image(image_local_path)
        
        imageLabel = self.builder.get_object("imageIndexLabel")
        imageLabel.set_text("Image " + str(image_index))
        imageLabel = self.builder.get_object("imageName")
        imageLabel.set_text(image.get_name())
        imageLabel = self.builder.get_object("imageResolution")
        imageLabel.set_text(image.get_width() + " x " + image.get_height())
        imageLabel = self.builder.get_object("imageFormat")
        imageLabel.set_text(image.get_format())
        imageLabel = self.builder.get_object("imageUrl")
        imageLabel.set_uri(url)
        imageLabel.set_label(url)
    
    def download_image(self, url):
        image_local_path = os.path.join(self.local_path_dir, url.split('/')[-1])
        try:
            urllib.urlretrieve(url, image_local_path)
            print "Info: Downloaded image from '" + url + "' into temporary image '" + self.local_path_dir + "'"
            
            return image_local_path
        except:
            sys.exit("Error: Could not download image from '" + url + "'")
        
    def resize_and_set_image(self, image_local_path, width = 600, height = 450):
        gtkImage = self.builder.get_object('image')
        pixbuf = Pixbuf.new_from_file_at_size(image_local_path, width, height)
        gtkImage.set_from_pixbuf(pixbuf)
        gtkImage.show()
    
    def exists_images_directory(self):
        return os.path.isdir(PATH_IMAGES_DIR)
    
    def create_images_directory(self):
        try:
            os.mkdir(PATH_IMAGES_DIR)
            print "Info: Created images directory '" + PATH_IMAGES_DIR + "'"
            
            return True
        except:
            sys.exit("Error: Directory '" + PATH_IMAGES_DIR + "' could not be created")
    
def main():
    main_window = Wallhaven_GUI()
    Gtk.main()
    
    return 0

if __name__ == '__main__':
    main()
