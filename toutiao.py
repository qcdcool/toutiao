# coding:utf-8
# @desc 开发者头条爬虫
# @author qcdcool@gmail.com
# @date 2016-1-10

import sys
import urllib2
import re
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
		print "启动爬虫..."
		while page < total:
			full_url = url % (page)
			subject_content = self.download(full_url)
			if subject_content is None:
				break
			subject_datas = self.parseSubject(subject_content)
			fout = open("toutiao.io/subjects_%d.md" % page, 'a+')
			fout.write("#开发者头条 第 %d 页\n" % page)
			fout.close()
			print "爬取第 %s 页数据..." % page
			for key in subject_datas:
				post_content = self.download(subject_datas[key]['url'])
				post_datas = self.parsePost(post_content)
				if len(post_datas) == 0:
					continue

				datas = {}
				datas['subject'] = subject_datas[key]['title']
				datas['url'] = subject_datas[key]['title']
				datas['posts'] = post_datas
				self.outputMarkdown(datas, page)
			page = page + 1
		print "爬虫任务结束..."
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
		num = 1
		for subject in subjects:
			subject_data = {}
			subject_data['title'] = subject.get_text()
			subject_data['url'] = "http://toutiao.io/%s" % subject['href']
			key = "subject%d" % num
			subject_datas.setdefault(key, subject_data)
			num = num + 1
		return subject_datas

	# 解析文章
	def parsePost(self, content):
		post_datas = {}
		soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
		posts = soup.find_all('div', class_="post")
		num = 1
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
	def outputMarkdown(self, datas, page):
		fout = open("toutiao.io/subjects_%d.md" % page, 'a+')
		fout.write("----------------\n")
		fout.write("##[%s](%s)\n" % (datas['subject'].encode('utf-8'), datas['url']))
		for key in datas['posts']:
			line = "-	[%s](%s)\n"%(datas['posts'][key]['title'].encode('utf-8'), datas['posts'][key]['url'])
			fout.write(line)
			fout.write("\n")
		fout.close()

# 爬虫入口
if __name__ == '__main__':
	root_url = "http://toutiao.io/explore?page=%d"
	obj_spider = ToutiaoMain()
	obj_spider.craw(root_url)