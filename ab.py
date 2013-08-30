#coding=utf8
import sys
import urllib
import urllib2
import threading
import Queue
import time
import re
from sgmllib import SGMLParser
from optparse import OptionParser

makepolo_url = "http://caigou.makepolo.com/spc_new.php?search_flag=0&q="
alibaba_url =  "http://s.1688.com/selloffer/offer_search.htm?n=y&keywords="


class QueryResultParser(SGMLParser):
    def __init__(self, source):
        self.source = source
        self.is_title = 0
        self.title_list = []
        self.href_list = []
        SGMLParser.__init__(self)

    def reset(self):
        SGMLParser.reset(self)

    def start_a(self, attrs):
        attr_dict = dict(attrs)
        if self.source == "makepolo":
            if attr_dict.has_key('data-num') and attr_dict['data-num'] == "1":
                self.is_title = 1
                self.href_list.append(attr_dict['href'])
        if self.source == "1688":
            if attr_dict.has_key('offer-stat') and attr_dict['offer-stat'] == "title":
                self.is_title = 1
                self.href_list.append(attr_dict['href'])

    def end_a(self):
        self.is_title = 0
                
    def handle_data(self, text):
        if self.is_title:
            text = unicode(text, "gbk")
            utf8_text = text.encode('utf-8')
            self.title_list.append(urllib.unquote(text))
    

class ThreadPool(object):
    def __init__(self, url_list, req_number, thread_num):
		self.work_queue = Queue.Queue()
		self.threads = []
		self.__init_work_queue(url_list)
		self.__init_thread_pool(thread_num)
    """
		initialize threads
    """
    def __init_thread_pool(self, thread_num):
		for i in range(thread_num):
			self.threads.append(MyThread(self.work_queue))
	
    """
		initialize work queue
    """

    def __init_work_queue(self, url_list):
        for item in url_list:
            self.add_job(do_job, item)

    """
		add a job to the queue
    """
    def add_job(self, func, args):
		self.work_queue.put((func, args))
	
    """
		wait for all the threads to be completed
    """
    def wait_all_complete(self):
		for item in self.threads:
			if item.isAlive():
				item.join()

class MyThread(threading.Thread):
	def __init__(self, work_queue):
		threading.Thread.__init__(self)
		self.work_queue = work_queue
		self.start()

	def run(self):
		while True:
			try:
				do, args = self.work_queue.get(block=False)
				do(args)
				self.work_queue.task_done()#notify the completement of the job
			except:
				break

ERROR_NUM = 0

def do_job(args):
    try:
        sock = urllib2.urlopen(args)
        response = sock.read()
        sock.close()
        if 'makepolo.com' in args:
            source = "makepolo"
        if "1688.com" in args:
            source = "1688"
        query_parser = QueryResultParser(source)
        query_parser.feed(response)
        for item in query_parser.href_list:
            print item
        for item in query_parser.title_list:
            print item
    except Exception, e:
		print e
		global ERROR_NUM
		ERROR_NUM += 1


def parse():
	"""parse the args"""
	parser = OptionParser(description="The scripte is used to simulate apache benchmark(sending requests and testing the server)")
	parser.add_option("-n", "--number", dest="num_of_req", action="store", help="Number of requests you want to send", default=1)
	parser.add_option("-c", "--concurrent", dest="con_req", action="store", help="Number of concurrent requests you set", default=1)
	parser.add_option("-u", "--url", dest="urlpth", action="store", help="The url of server you want to send to")
	(options, args) = parser.parse_args()
	return options

def main():
    """main function"""
    start = time.time()
    options = parse()
    
    if not options.urlpth:
    	print 'Need to specify the parameter option "-u"!'
    if '-h' in sys.argv or '--help' in sys.argv:
    	print __doc__
    
    # 打开文件，并将文件中的内容找出，拼成url
    with open("query.txt") as f:
        query_text_list = f.readlines()
        query_url_list = []
        for item in query_text_list:
            item = item[:-1]  # 去除回车符
            if "makepolo.com" in options.urlpth:
                query_url = makepolo_url + urllib.quote(item)
                print query_url
                query_url_list.append(query_url)
            if "1688.com" in options.urlpth:
                item = unicode(item, "utf-8")
                gbk_item = item.encode("gbk")
                query_url = alibaba_url + urllib.quote(gbk_item)
                print query_url
                query_url_list.append(query_url)
    
	tp = ThreadPool(query_url_list, int(options.num_of_req), int(options.con_req))
	tp.wait_all_complete()
	end = time.time()

if __name__ == '__main__':
	main()
