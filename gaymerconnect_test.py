from selenium import webdriver
import sys
import string
import time
import random
import logging

class TestSuite():
    """Defines the tests to be run upon init.
       Run tests by calling run() method

    """
    def __init__(self):
        """Preload browser, generate user credentials and define tests"""
        #set up logging
        logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG)
        #spawn a browser
        self.browser = self._generate_browser()
        self._setup()

    def _generate_browser(self):
        """Load Firefox and set the self.browser variable"""
        browser = webdriver.Chrome()
        logging.debug("Launching browser...")
        return browser

    def run(self):
        """Runs tests, then runs cleanup.
           Returns tuple of dicts, failures and passes.

        """
        #run tests
        failures = []
        try:
            for test in self.tests:
                (name, func) = test
                logging.info("{0} - Starting test...".format(name))
                try:
                    func()
                except AssertionError:
                    logging.warning("{0} - Test failed!".format(name))
                    failures.append(name)
                finally:
                    self.browser.save_screenshot("{0}.png".format(func.__name__))
                    html = open("{0}.html".format(func.__name__), 'w')
                    html.write(self.browser.page_source.encode('ascii', 'ignore'))
                    html.close()
                    logging.debug("Sleeping for five seconds")
                    time.sleep(5)
        except:
            pass
        #run cleanup
        try:
            for task in self.cleanup:
                (name, func) = task
                logging.info("{0} - Cleaning up...".format(name))
                try:
                    func()
                except:
                    logging.warning("{0} - Cleanup failed!".format(name))
                    failures.append(name)
                finally:
                    self.browser.save_screenshot("{0}.png".format(func.__name__))
                    html = open("{0}.html".format(func.__name__), 'w')
                    html.write(self.browser.page_source.encode('ascii', 'ignore'))
                    html.close()
                    logging.debug("Sleeping for five seconds")
                    time.sleep(5)
        finally:
            self.browser.quit()

        passes = [x for (x, f) in (self.tests + self.cleanup) if x not in failures]
        return (failures, passes)

class GaymerConnectTestSuite(TestSuite):
    """Tests for GaymerConnect.com"""

    def _setup(self):
        """Define the tests"""
        self.base_url = "http://www.gaymerconnect.com"
        self.tests = (('Create User', self.create_user),
                      ('Create Group', self.create_group),
                      ('Create Post', self.create_post),
                      ('Comment on Post', self.comment_on_post))
        self.cleanup = (('Delete Comment', self.delete_comment),
                        ('Delete Post', self.delete_post),
                        ('Delete Group', self.delete_group),
                        ('Delete User', self.delete_user))

    def _generate_random_characters(self, length):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) \
                       for x in range(length))

    def _generate_email(self):
        # Generate new email address
        random_chars = self._generate_random_characters(12)
        email = "{}@somedomain.com".format(random_chars)
        logging.debug("Email is {}".format(email))
        return email

    def create_user(self):
        """Creates new gaymerconnect.com user"""
        self.email = self._generate_email()
        self.password = "real_password"
        self.browser.get(self.base_url + "/users/sign_in")
        logging.info("Getting {}".format(self.base_url + "/users/sign_in"))
        elem = self.browser.find_element_by_link_text("Create an account")
        elem.click()
        elem = self.browser.find_element_by_id("user_email")
        elem.click()
        elem.send_keys(self.email)
        logging.debug("Email set")
        elem = self.browser.find_element_by_id("user_password")
        elem.click()
        elem.send_keys(self.password)
        logging.debug("Password set")
        elem = self.browser.find_element_by_id("user_password_confirmation")
        elem.click()
        elem.send_keys(self.password)
        logging.debug("Password confirmed")
        elem.submit()
        logging.info("Submitting new user form")
        assert "Level Up" in self.browser.page_source.encode('ascii', 'ignore')

    def create_group(self):
        """Create new private group"""
        self.group_name = self._generate_random_characters(16)
        self.browser.get(self.base_url + "/groups/new")
        self.browser.find_element_by_id("group_name").clear()
        self.browser.find_element_by_id("group_name").send_keys(self.group_name)
        logging.debug("Group name set: {}".format(self.group_name))
        self.browser.find_element_by_id("group_private").click()
        self.browser.find_element_by_name("commit").click()
        assert "Group created" in self.browser.page_source.encode('ascii', 'ignore')

    def create_post(self):
        """Create a post in the group we just made"""
        self.browser.get(self.base_url + "/groups/{0}/posts/new".format(self.group_name))
        self.browser.find_element_by_id("group_post_title").clear()
        self.browser.find_element_by_id("group_post_title").send_keys("Test Post")
        self.browser.find_element_by_id("group_post_content").clear()
        self.browser.find_element_by_id("group_post_content").send_keys("Test Message")
        self.browser.find_element_by_id("group_post_content").submit()
        assert "Post created" in self.browser.page_source.encode('ascii', 'ignore')

    def comment_on_post(self):
        """Create a comment in the post we just made"""
        self.browser.get(self.base_url + "/groups/{0}".format(self.group_name))
        self.browser.find_element_by_link_text("Test Post").click()
        self.browser.find_element_by_id("group_comment_content").clear()
        self.browser.find_element_by_id("group_comment_content").send_keys("Test Comment")
        self.browser.find_element_by_id("group_comment_content").submit()
        assert "Comment posted" in self.browser.page_source.encode('ascii', 'ignore')

    def delete_comment(self):
        """Delete the comment that we just made"""
        self.browser.get(self.base_url + "/groups/{0}".format(self.group_name))
        self.browser.find_element_by_link_text("Test Post").click()
        self.browser.find_element_by_css_selector("td.span2 > a.btn.btn-danger").click()
        self.browser.switch_to_alert().accept()
        time.sleep(5)
        assert "Comment deleted" in self.browser.page_source.encode('ascii', 'ignore')

    def delete_post(self):
        """Delete the post that we just made"""
        self.browser.get(self.base_url + "/groups/{0}".format(self.group_name))
        self.browser.find_element_by_link_text("Test Post").click()
        self.browser.find_element_by_link_text("Delete").click()
        self.browser.switch_to_alert().accept()
        time.sleep(5)
        assert "Post deleted" in self.browser.page_source.encode('ascii', 'ignore')

    def delete_group(self):
        """Delete the group that we made"""
        self.browser.get(self.base_url + "/groups/{0}".format(self.group_name))
        self.browser.find_element_by_link_text("Delete Group").click()
        self.browser.switch_to_alert().accept()
        time.sleep(5)
        assert "Group deleted" in self.browser.page_source.encode('ascii', 'ignore')

    def delete_user(self):
        """Delete the user that we made"""
        self.browser.get(self.base_url + "/users/edit")
        logging.debug('Clicking on Settings Tab')
        self.browser.find_element_by_link_text("Settings").click()
        logging.debug('Clicking on Cancel my account')
        self.browser.find_element_by_link_text("Cancel my account").click()
        logging.debug('Accepting alert')
        self.browser.switch_to_alert().accept()
        time.sleep(5)
        assert "Come back soon" in self.browser.page_source.encode('ascii', 'ignore')

if __name__=="__main__":
    gaymer_connect_test = GaymerConnectTestSuite()
    failures, passes = gaymer_connect_test.run()
    print "There were {0} passes".format(len(passes))
    print passes
    if len(failures) > 0:
        print "There were {0} failures".format(len(failures))
        print failures
        sys.exit(1)
    else:
        sys.exit(0)
