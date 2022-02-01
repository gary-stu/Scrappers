from time import sleep

import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Edge
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from argparse import ArgumentParser
from os import path, remove, makedirs
from shutil import rmtree
import logging


class Scrapper:
	def __init__(self, args_array):
		# Init logger
		self.logger = logging.getLogger('Scrapper')
		formatter = logging.Formatter('%(asctime)s - %(name)s:%(levelname)s - %(message)s')
		stream_handler = logging.StreamHandler()
		stream_handler.setFormatter(formatter)
		self.logger.addHandler(stream_handler)

		if args_array.log_path != '':
			file_handler = logging.FileHandler(args.log_path, encoding='utf-8')
			file_handler.setFormatter(formatter)
			self.logger.addHandler(file_handler)

		if args_array.verbose:
			self.logger.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.INFO)

		self.logger.info('Initializing scrapper class')

		# Init constants
		self.url = 'https://hanime.tv/browse/images'
		self.args = args_array

		# Init variables
		self.media = False
		self.nsfw = False
		self.furry = False
		self.futa = False
		self.yaoi = False
		self.yuri = False
		self.traps = False
		self.irl = False
		self.overwrite = False
		self.create = False
		self.verbose = False
		self.nb_page = 1
		self.images_to_download = []
		self.dest_path = ''
		self.driver = None

		# Tags selection
		number_tag_selected = 0
		if self.args.media:
			self.media = True
			self.logger.info('Downloading media tag')
			number_tag_selected = number_tag_selected + 1

		if self.args.nsfw:
			self.nsfw = True
			self.logger.info('Downloading nsfw-general tag')
			number_tag_selected = number_tag_selected + 1

		if self.args.furry:
			self.furry = True
			self.logger.info('Downloading furry tag')
			number_tag_selected = number_tag_selected + 1

		if self.args.futa:
			self.futa = True
			self.logger.info('Downloading futa tag')
			number_tag_selected = number_tag_selected + 1

		if self.args.yaoi:
			self.yaoi = True
			self.logger.info('Downloading yaoi tag')
			number_tag_selected = number_tag_selected + 1
			
		if self.args.yuri:
			self.yuri = True
			self.logger.info('Downloading yuri tag')
			number_tag_selected = number_tag_selected + 1
			
		if self.args.traps:
			self.traps = True
			self.logger.info('Downloading traps tag')
			number_tag_selected = number_tag_selected + 1
			
		if self.args.irl:
			self.irl = True
			self.logger.info('Downloading irl-3d tag')
			number_tag_selected = number_tag_selected + 1
			
		if number_tag_selected == 0:
			self.logger.info('No tags selected, defaulting to download nsfw-general')
			self.nsfw = True

		self.nb_page = self.args.number
		self.logger.info('number of pages to download : "%i"', self.nb_page)

		# Path where the files will be saved
		self.dest_path = self.args.path
		self.logger.info('Destination path : "%s"', self.dest_path)
		if not(path.isdir(self.dest_path)):
			self.logger.error('"%s" is not a valid path', self.dest_path)
			if self.args.create:
				self.create_folder()
			else:
				exit(10)
		else:
			if self.args.delete:
				self.logger.info('Deleting folder "%s"', self.dest_path)
				try:
					rmtree(self.dest_path)
				except PermissionError as err:
					self.logger.error(err)
					exit(11)
				self.create_folder()
			else:
				self.logger.info('"%s" folder already exists')

		if args.overwrite:
			self.overwrite = True
			self.logger.info('Overwriting existing files')

		# browser
		self.browser = self.args.browser.lower()
		self.verbose = self.args.verbose
		if not(self.browser in ['firefox', 'chrome', 'edge']):
			self.logger.error('Use "firefox", "chrome" or "edge" browser driver')
			exit(12)
			
		self.logger.info('Browser driver : "%s", verbose mode : %s', self.browser, self.verbose)
		self.driver = self.init_driver()

		# Program
		self.start_driver()
		sleep(3)
		self.click_tags()
		self.scrape_driver()
		self.close_driver()
		self.download_all()
		self.write_fssort_ini()

	"""

	"""
	def init_driver(self):
		self.logger.info('Initializing selenium driver')
		if self.browser == 'firefox':
			firefox_options = FirefoxOptions()
			firefox_options.headless = not self.verbose
			driver = Firefox(service=FirefoxService(GeckoDriverManager().install(), log_path=path.devnull), options=firefox_options)
			return driver

		elif self.browser == 'chrome':
			chrome_options = ChromeOptions()
			chrome_options.headless = not self.verbose
			driver = Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
			return driver

		elif self.browser == 'edge':
			edge_option = EdgeOptions()
			edge_option.use_chromium = True
			edge_option.headless = not self.verbose
			driver = Edge(service=EdgeService(EdgeChromiumDriverManager(log_level=logging.INFO).install()), options=edge_option)
			# Note : DriverManager(log_level=X) due to bug https://github.com/SergeyPirogov/webdriver_manager/issues/269
			return driver
		else:
			return None

	"""
	
	"""
	def create_folder(self):
		self.logger.info('Creating folder "%s"', self.dest_path)
		try:
			makedirs(self.dest_path)
		except (OSError, PermissionError) as err:
			self.logger.error(err)
			exit(12)

	"""
	
	"""
	def start_driver(self):
		self.logger.info('Starting selenium driver. Loading page {}'.format(self.url))
		self.driver.get(self.url)

	"""
	
	"""
	def click_tags(self):
		self.logger.info('Selecting chosen tags')
		if not self.media:
			self.logger.debug('Deselecting media tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[1]/div').click()
			sleep(1)
			
		if not self.nsfw:
			self.logger.debug('Deselecting nsfw tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[2]/div').click()
			sleep(1)
			
		if self.furry:
			self.logger.debug('selecting furry tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[3]/div').click()
			sleep(1)
			
		if self.futa:
			self.logger.debug('selecting futa tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[4]/div').click()
			sleep(1)
			
		if self.yaoi :
			self.logger.debug('selecting yaoi tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[5]/div').click()
			sleep(1)
			
		if self.yuri:
			self.logger.debug('selecting yuri tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[6]/div').click()
			sleep(1)
			
		if self.traps:
			self.logger.debug('selecting traps tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[7]/div').click()
			sleep(1)
		
		if self.irl:
			self.logger.debug('selecting irl tag')
			self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[3]/div[8]/div').click()
			sleep(1)
		sleep(2)

	"""
	
	"""
	def scrape_page(self):
		self.logger.info('scraping current page')
		for i in range(1, 101):
			try:
				image = self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[5]/a[{0}]'.format(i)).get_attribute("href")
				self.images_to_download.append(image)
				self.logger.debug('%i : "%s"', i, image)
			except NoSuchElementException:
				self.logger.debug('%i : pass', i)
				pass

	"""
	
	"""
	def next_page(self):
		self.logger.info('Next page')
		self.driver.find_element(by=By.XPATH, value='//*[@id="app"]/div[4]/main/div/div/div/div[4]/button[3]/div').click()
		sleep(2)

	"""
	
	"""
	def scrape_driver(self):
		self.logger.info('Scraping {} pages'.format(self.nb_page))
		for i in range(1, self.nb_page + 1):
			self.logger.info('Page %i', i)
			self.scrape_page()
			self.next_page()

	"""
	
	"""
	def download_picture(self, url):
		file_name = url.split('/')[-1]
		file_path = path.join(self.dest_path, file_name)
		file_exists = path.isfile(file_path)
		if (not file_exists) or (file_exists and self.overwrite):
			self.logger.debug('downloading "%s"', file_path)
			with open(file_path, 'wb') as file:
				response = requests.get(url, stream=True)
				if not response.ok:
					self.logger.error(response)
				
				for block in response.iter_content(1024):
					if not block:
						break
					file.write(block)
		else:
			self.logger.debug('"%s" already exists', file_path)

	"""
	
	"""
	def download_all(self):
		self.logger.info('Downloading files')
		for url in self.images_to_download:
			self.download_picture(url)

	"""
	
	"""
	def close_driver(self):
		self.logger.info('Closing selenium driver')
		self.driver.close()

	"""
	
	"""
	def write_fssort_ini(self):
		self.logger.info('Writing "fssort.ini" file')
		file_path = path.join(self.dest_path, 'fssort.ini')
		if path.isfile(file_path):
			remove(file_path)
			
		with open(file_path, 'w') as f:
			for line in self.images_to_download:
				file_name = line.split('/')[-1]
				f.write(file_name + '\n')
				

if __name__ == '__main__':
	
	parser = ArgumentParser(description='HA scrapper')
	parser.add_argument(
		'-m', '--media',
		dest='media',
		action='store_true',
		help='Download media tag',
	)

	parser.add_argument(
		'-nsfw', '--nsfw-general',
		dest='nsfw',
		action='store_true',
		help='Download nsfw-general tag',
	)

	parser.add_argument(
		'-fr', '--furry',
		dest='furry',
		action='store_true',
		help='Download furry tag',
	)

	parser.add_argument(
		'-ft', '--futa',
		dest='futa',
		action='store_true',
		help='Download futa tag',
	)

	parser.add_argument(
		'-ya', '--yaoi',
		dest='yaoi',
		action='store_true',
		help='Download yaoi tag',
	)

	parser.add_argument(
		'-yu', '--yuri',
		dest='yuri',
		action='store_true',
		help='Download yuri tag',
	)

	parser.add_argument(
		'-t', '--traps',
		dest='traps',
		action='store_true',
		help='Download traps tag',
	)

	parser.add_argument(
		'-i', '--irl',
		dest='irl',
		action='store_true',
		help='Download irl-3d tag',
	)

	parser.add_argument(
		'-n', '--pages-number',
		dest='number',
		type=int,
		action='store',
		help='number of pages to download',
		default=1
	)
	
	parser.add_argument(
		'-o', '--overwrite-files',
		dest='overwrite',
		action='store_true',
		help='overwrite already existing files'
	)

	parser.add_argument(
		'-p', '--path',
		dest='path',
		action='store',
		help='destination path',
		default='./files'
	)
	
	parser.add_argument(
		'-c', '--create-if-not-exist',
		dest='create',
		action='store_true',
		help='create path if it doesn\'t exist'
	)
	
	parser.add_argument(
		'-d', '--delete-folder',
		dest='delete',
		action='store_true',
		help='delete folder'
	)

	parser.add_argument(
		'-b', '--browser',
		dest='browser',
		action='store',
		help='Browser driver to use',
		default='firefox'
	)
	
	parser.add_argument(
		'-v', '--verbose',
		dest='verbose',
		action='store_true',
		help='Run in verbose mode'
	)

	parser.add_argument(
		'--log-path', '-l',
		dest='log_path',
		action='store',
		help='log path',
		default=''
	)
	
	args = parser.parse_args()
	sc = Scrapper(args)
