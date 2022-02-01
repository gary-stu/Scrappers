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
from os import path, remove
import logging


class LNScrapper:

    """
    Class constructor
    """
    def __init__(self, args_array):
        # Set up logger
        self.logger = logging.getLogger("LNScrapper")
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

        # initialize constants constants
        self.URL = 'https://www.reddit.com/r/LightNovels/wiki/upcomingreleases'
        self.args = args_array

        # Initialize variables
        self.csv_text = 'Month;Day;Series Name;Volume Number;Release\n'
        self.driver = self.init_driver()

        # Execute code
        self.start_driver()
        self.parse_webpage()
        self.close_driver()
        self.save_csv()

    """
    Init the Selenium driver
    """
    def init_driver(self):
        self.logger.info('Initializing selenium driver')

        headless = not self.args.verbose
        self.logger.debug('Verbose mode : "{}"'.format(self.args.verbose))

        browser = self.args.browser.lower()
        self.logger.debug('Browser : "{}"'.format(browser))

        if browser == 'firefox':
            firefox_options = FirefoxOptions()
            firefox_options.headless = headless
            driver = Firefox(service=FirefoxService(GeckoDriverManager().install(), log_path=path.devnull), options=firefox_options)
            return driver

        elif browser == 'chrome':
            chrome_options = ChromeOptions()
            chrome_options.headless = headless
            driver = Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            return driver

        elif browser == 'edge':
            edge_option = EdgeOptions()
            edge_option.headless = headless
            driver = Edge(service=EdgeService(EdgeChromiumDriverManager(log_level=logging.INFO).install()), options=edge_option)
            # Note : DriverManager(log_level=X) due to bug https://github.com/SergeyPirogov/webdriver_manager/issues/269
            return driver
        else:
            self.logger.error('Driver error')
            return None

    """
    Start the driver and load the page
    """
    def start_driver(self):
        self.logger.info('Starting selenium driver')
        self.logger.debug('Loading page "{}"'.format(self.URL))
        self.driver.get(self.URL)

    """
    Parse the webpage to get relevant information
    """
    def parse_webpage(self):
        self.logger.info('Starting to parse webpage')
        elem_h3 = self.driver.find_elements(by=By.XPATH, value='//h3')
        tables = self.driver.find_elements(by=By.XPATH, value='//h3/following-sibling::table')

        for i in range(0, len(elem_h3)):
            self.logger.debug('Table "{}"'.format(elem_h3[i].text))
            rows = tables[i].find_elements(by=By.XPATH, value='.//tbody/tr')
            for row in rows:
                cells = row.find_elements(by=By.XPATH, value='.//td')
                date = cells[0].text
                date_split = date.split(' ')
                day = date_split[1]
                month = date_split[0]
                name = cells[1].text
                number = cells[2].text
                release = cells[4].text

                line = '{};{};{};{};{}'.format(month, day, name, number, release)
                self.logger.debug('{}'.format(line))

                self.csv_text = self.csv_text + line + '\n'

    """
    Close the selenium driver
    """
    def close_driver(self):
        self.logger.info('Closing selenium driver')
        self.driver.close()

    """
    Save the csv file
    """
    def save_csv(self):
        filename = self.args.filename

        if path.exists(filename):
            self.logger.info('File "{}" already exists, deleting it'.format(filename))
            remove(filename)

        self.logger.info('Saving file "{}"'.format(filename))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.csv_text)


if __name__ == '__main__':
    # Args
    parser = ArgumentParser(description='Reddit scrapper for upcoming light novel releases')

    parser.add_argument(
        '--browser', '-b',
        dest='browser',
        action='store',
        help='Browser driver to use (firefox, chrome or edge). Defaults to firefox',
        default='firefox'
    )

    parser.add_argument(
        '--verbose', '-v',
        dest='verbose',
        action='store_true',
        help='Verbose mode',
    )

    parser.add_argument(
        '--filename', '-f',
        dest='filename',
        action='store',
        help='Filename of the saved csv file. Defaults to "data.csv"',
        default='data.csv'
    )

    parser.add_argument(
        '--log-path', '-l',
        dest='log_path',
        action='store',
        help='Log file path. does not log to a file if not set',
        default=''
    )

    args = parser.parse_args()
    sc = LNScrapper(args)
