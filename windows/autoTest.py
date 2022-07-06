import os
import sys
import json
import string
import random
import unittest
import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.service import Service as eService
from selenium.webdriver.chrome.service import Service as cService
from selenium.webdriver.safari.service import Service as sService

import elements as ui
from HTMLTestRunner_PY3 import HTMLTestRunner

__author__ = 'ashine02@gmail.com'
__version__ = '0.1'

class WarrantyCheckChrome(unittest.TestCase):
	def setUp(self):
		jsonFilePath = "ValidSerial.json"
		f = open(jsonFilePath)
		self.data = json.load(f)
		self.setupBrowser()
		# Accept all cookies
		self.driver.implicitly_wait(10)
		self.driver.get(ui.LINK)
		self.driver.find_element("id",ui.COOKIE_BTN_ID).click()
		# Find the input textField
		self.textarea = self.driver.find_element("id",ui.TEXTAREA_ID)

	def tearDown(self):
		self.driver.close()

	def setupBrowser(self):
		s = cService(r"./chromedriver")
		self.options = webdriver.ChromeOptions()
		self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
		self.driver = webdriver.Chrome(service=s,options=self.options)

	def randomStrGenerator(self, digit:int)->str:
		return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(digit))

	def randomSymGenerator(self, digit:int)->str:
		src_special = string.punctuation
		specialStr = random.sample(src_special,digit)
		random.shuffle(specialStr)
		return ''.join(specialStr)


	def testEmptyInput(self):
		self.textarea.click()
		self.textarea.clear()
		self.textarea.send_keys(Keys.ENTER)
		sleep(1)
		spans = self.driver.find_elements("class name",ui.SPAN_CLASS)
		self.assertNotEqual("display: none;",spans[0].get_attribute("style"),"Empty Msg is not shown")
		self.assertEqual("display: none;",spans[1].get_attribute("style"),"Should not show 'Too short' Msg")
		self.assertEqual("display: none;",spans[2].get_attribute("style"),"Should not show 'Invalid' Msg")


	def testInputLength(self):
		for i in range(1,6):
			self.textarea.click()
			self.textarea.clear()
			self.textarea.send_keys(self.randomStrGenerator(i))
			self.textarea.send_keys(Keys.ENTER)
			sleep(1)
			spans = self.driver.find_elements("class name",ui.SPAN_CLASS)
			self.assertEqual("display: none;",spans[0].get_attribute("style"),"Should not show 'Empty' Msg")
			self.assertNotEqual("display: none;",spans[1].get_attribute("style"),"'Too short' Msg is not shown")
			self.assertEqual("display: none;",spans[2].get_attribute("style"),"Should not show 'Invalid' Msg")

		# Test for input length == 6
		self.textarea.click()
		self.textarea.clear()
		self.textarea.send_keys(self.randomStrGenerator(6))
		self.textarea.send_keys(Keys.ENTER)
		sleep(1)
		spans = self.driver.find_elements("class name",ui.SPAN_CLASS)
		self.assertEqual("display: none;",spans[0].get_attribute("style"),"Should not show 'Empty' Msg")
		self.assertEqual("display: none;",spans[1].get_attribute("style"),"Should not show 'Too short' Msg")
		self.assertEqual("display: none;",spans[2].get_attribute("style"),"Should not show 'Invalid' Msg")

	def testInvalidInput(self):
		self.textarea.click()
		self.textarea.clear()
		input = self.randomSymGenerator(6)
		self.textarea.send_keys(input)
		self.textarea.send_keys(Keys.ENTER)
		sleep(1)
		spans = self.driver.find_elements("class name",ui.SPAN_CLASS)
		self.assertEqual("display: none;",spans[0].get_attribute("style"),"Should not show 'Empty' Msg")
		self.assertEqual("display: none;",spans[1].get_attribute("style"),"Should not show 'Too short' Msg")
		self.assertNotEqual("display: none;",spans[2].get_attribute("style"),f"Input '{input}', but the invalid Msg is not shown")

	def testLengthAndInvalidInput(self):
		for i in range(1,6):
			self.textarea.click()
			self.textarea.clear()
			input = self.randomSymGenerator(i)
			self.textarea.send_keys(input)
			self.textarea.send_keys(Keys.ENTER)
			sleep(1)
			spans = self.driver.find_elements("class name",ui.SPAN_CLASS)
			self.assertEqual("display: none;",spans[0].get_attribute("style"),"Should not show 'Empty' Msg")
			self.assertNotEqual("display: none;",spans[1].get_attribute("style"),"'Too short' Msg is not shown")
			self.assertNotEqual("display: none;",spans[2].get_attribute("style"),f"Input '{input}', but the invalid Msg is not shown")

	def testValidSerialNumber(self):
		for key, val in self.data.items():
			self.textarea.click()
			self.textarea.clear()
			self.textarea.send_keys(val)
			self.textarea.send_keys(Keys.ENTER)
			self.driver.implicitly_wait(15)
			serialNumber_found = True
			try:
				rst_item = self.driver.find_element("class name",ui.RST_ITEM_CLASS)
			except NoSuchElementException:
				serialNumber_found = False

			self.assertTrue(serialNumber_found == True, f"SerialNumber {val} not found")

class WarrantyCheckSafari(WarrantyCheckChrome):
	def setupBrowser(self):
		s = sService(r"/usr/bin/safaridriver")
		self.driver = webdriver.Safari(service=s)


class WarrantyCheckEdge(WarrantyCheckChrome):
	def setupBrowser(self):
		s = eService(r"./msedgedriver")
		self.options = webdriver.EdgeOptions()
		self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
		self.driver = webdriver.Edge(service=s, options=self.options)

if __name__ == "__main__":

	suite = unittest.TestSuite()
	suite.addTest(WarrantyCheckChrome("testEmptyInput"))
	suite.addTest(WarrantyCheckChrome("testInputLength"))
	suite.addTest(WarrantyCheckChrome("testInvalidInput"))
	suite.addTest(WarrantyCheckChrome("testLengthAndInvalidInput"))
	suite.addTest(WarrantyCheckChrome("testValidSerialNumber"))

	if sys.platform == "win32":
		suite.addTest(WarrantyCheckEdge("testEmptyInput"))
		suite.addTest(WarrantyCheckEdge("testInputLength"))
		suite.addTest(WarrantyCheckEdge("testInvalidInput"))
		suite.addTest(WarrantyCheckEdge("testLengthAndInvalidInput"))
		suite.addTest(WarrantyCheckEdge("testValidSerialNumber"))

	if sys.platform == "darwin":
		suite.addTest(WarrantyCheckSafari("testEmptyInput"))
		suite.addTest(WarrantyCheckSafari("testInputLength"))
		suite.addTest(WarrantyCheckSafari("testInvalidInput"))
		suite.addTest(WarrantyCheckSafari("testLengthAndInvalidInput"))
		suite.addTest(WarrantyCheckSafari("testValidSerialNumber"))

	timeFormat = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
	report_title = "Warranty Test"
	desc = "Test if the 'Warranty Checking' functional"
	report_file = f"test_report_{timeFormat}.html"

	with open(report_file, 'wb') as report:
		runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
		runner.run(suite)

