import os
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from time import gmtime, strftime
import os
import json
URLS = "urls.txt"
MSG = "message.txt"
def run():
	print("Please make sure you did write URLs of recipients on seperate lines of " + URLS + " and closed the file!")
	print("Please make sure your " + MSG + " is not empty and close the file!")
	with open(URLS) as f:
	    content = f.readlines()
	# you may also want to remove whitespace characters like `\n` at the end of each line
	content = [x.strip() for x in content]
	with open(MSG, 'r') as content_file:
	    message = content_file.read()
	urls = []
	for url in content:
		original_url = url
		fb_id = re.sub(r'.*com\/', '', url)
		fb_id = re.sub(r'.*id=', '', fb_id)
		fb_id = re.sub(r'\/', '', fb_id)
		urls.append({"url": original_url, "fb_id": fb_id, "mbasic_url": "https://mbasic.facebook.com/" + fb_id})
	print("Facebook Login ...")
	username = raw_input("Facebook Username/Email: ")
	password = raw_input("Password: ")
	time_string = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = (
	    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
	    "(KHTML, like Gecko) Chrome/15.0.87"
	)
	results = []
	# driver = [None] * len(urls)
	driver = webdriver.PhantomJS(desired_capabilities=dcap)
	driver.set_page_load_timeout(6)
	# Login
	driver.get("https://mbasic.facebook.com")
	email_element = driver.find_element_by_name("email")
	email_element.send_keys(username)
	pass_element = driver.find_element_by_name("pass")
	pass_element.send_keys(password)
	pass_element.send_keys(Keys.ENTER)
	if "save-device" in driver.current_url or "home.php" in driver.current_url:
		print("Logged in as " + username)
		for idx, item in enumerate(urls):
			driver.get(item['mbasic_url'])
			inbox_url = driver.find_element_by_xpath("//a[contains(@href,'messages/thread')]").get_attribute('href')
			if inbox_url:
				driver.get(inbox_url)
				t = driver.find_element_by_name("body")
				if t:
					t.send_keys(message)
					send_btn = driver.find_element_by_name('send')
					send_btn.click()
					time.sleep(3)
					if "send_success" in driver.current_url:
						print(strftime("%Y-%m-%d-%H-%M-%S", gmtime()) + ": " + username + " sent a message to " + item['fb_id'])
						results.append(item['mbasic_url'] + "," + "success")
					else:
						print("Failed to send from: " + username + " to: " + item['fb_id'])
						results.append(item['mbasic_url'] + "," + "failed")
				else:
					print("Textbox not found when sending from: " + username + " to: " + item['fb_id'])
					results.append(item['mbasic_url'] + "," + "failed")
			else:
				print("Not found mbasic_url when sending from: " + username + " to: " + item['fb_id'])
				results.append(item['mbasic_url'] + "," + "failed")
		output = open("result/" + username + "_" + time_string + ".txt", 'w')
		for item in results:
  			output.write("%s\n" % item)
  		output.close()
	else:
		print("Failed to login for: " + username)
	return
if __name__ == '__main__':
    run()
