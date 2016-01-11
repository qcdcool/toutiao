# coding:utf-8
# @desc IT博客大学习爬虫
# @author qcdcool@gmail.com
# @date 2016-1-12

import sys
import urllib2
import re
import datetime
import HTMLParser
from bs4 import BeautifulSoup
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class ItblogMain(object):

	def parseCategory(self, root_url):
		if root_url is None:
			return

		category_content = self.download(root_url)
		if category_content is None:
			return
		soup = BeautifulSoup(category_content, 'html.parser', from_encoding='utf-8')
		categories = soup.find('div', class_="nav").find_all('a', href=re.compile(r"/it/category/\d+"))
		if len(categories) < 1:
			return None
		num = 1
		category_datas = {}
		for category in categories:
			category_data = {}
			category_data['title'] = category.get_text()
			category_data['url'] = "http://blogread.cn%s" % category['href']
			key = "category%d" % num
			category_datas.setdefault(key, category_data)
			num = num + 1

		return category_datas

	# 爬虫
	def craw(self, url):
		category_datas = self.parseCategory(url)
		for key in category_datas:
			catList = category_datas[key]['url'].split('/')
			catnum = int(catList[-1])
			post_page = 1
			while 1:
				fout = open("posts/categorys_%d.md" % catnum, 'a+')
				fout.write("#IT博客大学习 %s 第 %d 页\n" % (category_datas[key]['title'], post_page))
				fout.close()
				print "%s 爬取主题: %s 第 %d 页数据..." % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), category_datas[key]['title'], post_page)
				post_url = "%s/%d" % (category_datas[key]['url'], post_page);
				print post_url
				post_content = self.download(post_url)

				if post_content is None:
					break;

				post_data = self.parsePost(post_content, post_page)
				if post_data is None:
					break;

				self.outputMarkdown(post_data, category_datas[key], catnum, post_page)
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

	# 解析文章
	def parsePost(self, html, post_page):
		post_datas = {}
		html_parser = HTMLParser.HTMLParser()
		content = html_parser.unescape(html)
		soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
		posts = soup.find('div', class_="cateArtBox").find_all('div', class_="box")
		count = len(posts)
		if count < 1:
			return None

		num = (post_page - 1) * count + 1
		for post in posts:
			temp = post.find('div', class_="title").find('a')
			post_data = {}
			post_data['title'] = temp.get_text()
			post_data['url'] = temp['href']
			post_data['summary'] = post.find('div', class_="profile").get_text().strip()
			key = "post%d" % num
			post_datas.setdefault(key, post_data)
			num = num + 1
		return post_datas

	# 输出markdown格式
	def outputMarkdown(self, post_data, subject_data, page, post_page):
		fout = open("posts/categorys_%d.md" % page, 'a+')
		fout.write("----------------\n")
		fout.write("##[%s 第 %d 页](%s)\n" % (subject_data['title'].encode('utf-8'), post_page, subject_data['url']))
		for key in post_data:
			fout.write("\n")
			fout.write("----------------\n")
			title = "####[%s](%s)\n"%(post_data[key]['title'].encode('utf-8'), post_data[key]['url'])
			fout.write("\n")
			fout.write(title)
			fout.write("\n")
			summary = "> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s\n" % post_data[key]['summary'].encode('utf-8') 
			fout.write(summary)
		fout.close()

# 爬虫入口
if __name__ == '__main__':
	root_url = "http://blogread.cn/it/"
	obj_spider = ItblogMain()
	print "%s 启动爬虫..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	obj_spider.craw(root_url)
	print "%s 爬虫任务结束..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	exit()
