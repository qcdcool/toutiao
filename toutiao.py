# coding:utf-8
# @desc 开发者头条爬虫
# @author qcdcool@gmail.com
# @date 2016-1-10

import sys
import urllib2
import re
import datetime
from bs4 import BeautifulSoup
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class ToutiaoMain(object):

	# 爬虫
	def craw(self, url):
		
		page = 1
		total = 26
		while (page < total):
			full_url = url % (page)
			subject_content = self.download(full_url)
			if subject_content is None:
				break
			subject_datas = self.parseSubject(subject_content)
			if subject_datas is None:
				break;
			fout = open("toutiao.io/subjects_%d.md" % page, 'a+')
			fout.write("#开发者头条 第 %d 页\n" % page)
			fout.close()
			print "%s 爬取第 %s 页数据..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),page)
			for key in subject_datas:
				post_page = 1
				while 1:
					post_url = "%s?page=%d" % (subject_datas[key]['url'], post_page);
					post_content = self.download(post_url)
					print post_url
					if post_content is None:
						break;

					post_data = self.parsePost(post_content, post_page)
					if post_data is None:
						break;

					print "%s 爬到主题: %s 第 %d 页" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), subject_datas[key]['title'].encode('utf-8'),post_page)
					self.outputMarkdown(post_data, subject_datas[key], page, post_page)
					post_page = post_page + 1

			page = page + 1
	# 下载
	def download(self, url):
			
		if url is None:
			return None

		request = urllib2.Request(url)

		# 头条需要用User-Agent header头，否则报403
		request.add_header('User-Agent', 'Mozilla/5.0')

		response = urllib2.urlopen(request)

		if response.getcode() != 200:
			return None

		return response.read()

	# 解析主题
	def parseSubject(self, content):
		subject_datas = {}
		soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
		subjects = soup.find_all('a', href=re.compile(r"/subjects/\d+"))
		if len(subjects) < 1:
			return None
		num = 1
		for subject in subjects:
			subject_data = {}
			subject_data['title'] = subject.get_text()
			subject_data['url'] = "http://toutiao.io%s" % subject['href']
			key = "subject%d" % num
			subject_datas.setdefault(key, subject_data)
			num = num + 1
		return subject_datas

	# 解析文章
	def parsePost(self, content, post_page):
		post_datas = {}
		soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
		posts = soup.find_all('div', class_="post")
		count = len(posts)
		if count < 1:
			return None

		num = (post_page - 1) * count + 1
		for post in posts:
			temp = post.find('h3', class_="title").find('a')
			post_data = {}
			post_data['title'] = temp.get_text()
			post_data['url'] = temp['href']
			key = "post%d" % num
			post_datas.setdefault(key, post_data)
			num = num + 1
		return post_datas

	# 输出markdown格式
	def outputMarkdown(self, post_data, subject_data, page, post_page):
		fout = open("toutiao.io/subjects_%d.md" % page, 'a+')
		fout.write("----------------\n")
		fout.write("##[%s 第 %d 页](%s)\n" % (subject_data['title'].encode('utf-8'), post_page, subject_data['url']))
		for key in post_data:
			line = "-	[%s](%s)\n"%(post_data[key]['title'].encode('utf-8'), post_data[key]['url'])
			fout.write(line)
			fout.write("\n")
		fout.close()

# 爬虫入口
if __name__ == '__main__':
	root_url = "http://toutiao.io/explore?page=%d"
	obj_spider = ToutiaoMain()
	print "%s 启动爬虫..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	obj_spider.craw(root_url)
	print "%s 爬虫任务结束..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	exit()