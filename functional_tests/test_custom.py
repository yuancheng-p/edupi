from cntapp.models import Directory
from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .base import FunctionalTest


class CustomSiteTestCase(FunctionalTest):

    def setUp(self):
        super().setUp()
        self.custom_page_url = self.server_url + '/custom/'

    def create_dir(self, dir_name):
        self.assertNotInBody(dir_name)
        base_url = self.browser.current_url

        # entered into a create page
        self.browser.find_element_by_id("create-directory").click()

        if base_url == self.custom_page_url:
            self.assertEqual(base_url + "#create", self.browser.current_url)
        else:
            self.assertEqual(base_url + "/create", self.browser.current_url)

        self.assertInBody("Create directory")

        # create directory
        self.browser.find_element_by_id('directory-name').send_keys(dir_name)
        self.browser.find_element_by_id('btn-create').send_keys(Keys.ENTER)

        # automatically go back to previous page
        self.assertEqual(base_url, self.browser.current_url)
        self.assertInBody(dir_name)

    def assertNotInDirectoryTable(self, text):
        self.assertNotIn(text, self.browser.find_element_by_css_selector('.table tbody').text)

    def assertInDirectoryTable(self, text):
        self.assertIn(text, self.browser.find_element_by_css_selector('.table tbody').text)

    def test_create_directories(self):
        # Alice wants to customize the web site, she enters into the custom home page
        self.browser.get(self.custom_page_url)
        self.assertInBody("Content Manager")

        # she is currently in the root dir, it's empty, she has to create a dir here
        # she clicks "Create Directory" to enter the create page,
        # she types a dir name in the input field and hit "ENTER",
        # then create form disappeared, and the name appears
        self.create_dir("primary")
        self.create_dir("secondary")

        # click the primary to go into this folder
        self.browser.find_element_by_link_text('primary').click()

        self.assertNotInDirectoryTable("primary")
        self.assertNotInDirectoryTable("secondary")

        self.create_dir("CP")
        self.create_dir("CE1")

        # enter in the next level
        self.browser.find_element_by_link_text('CP').click()
        self.assertNotInDirectoryTable("CP")

        self.create_dir("Math")
        self.create_dir("English")
        self.create_dir("French")

        self.browser.get(self.custom_page_url)
        self.assertInDirectoryTable("primary")
        self.assertNotInDirectoryTable("Math")

    def test_navigate_directory_path(self):
        from cntapp.tests.helpers import init_test_dirs
        init_test_dirs()
        self.assertEqual(6, Directory.objects.count())
        check_path = lambda path: self.assertEqual(path, self.browser.find_element_by_id("path").text)

        def enter_into_dir(dir_name):
            table = self.browser.find_element_by_class_name("table")
            table.find_element_by_link_text(dir_name).click()

        def back_to_dir(dir_name):
            path = self.browser.find_element_by_id("path")
            path.find_element_by_link_text(dir_name).click()

        self.browser.get(self.custom_page_url)
        enter_into_dir("a")
        check_path("> home > a")
        enter_into_dir("ab_a")
        check_path("> home > a > ab_a")
        enter_into_dir("ab_a_a")
        check_path("> home > a > ab_a > ab_a_a")
        self.browser.refresh()
        check_path("> home > a > ab_a > ab_a_a")

        back_to_dir("ab_a")
        check_path("> home > a > ab_a")
        back_to_dir("a")
        check_path("> home > a")
        back_to_dir("home")
        check_path("")
        enter_into_dir("a")
        check_path("> home > a")
        self.assertEqual(6, Directory.objects.count())

    def test_edit_directory(self):
        from cntapp.tests.helpers import init_test_dirs
        init_test_dirs()
        ## Let's get edit dir "a", and change it's name to primary

        # go into the root dirs page
        self.browser.get(self.custom_page_url)
        self.assertNotInBody("primary")

        edit_elements = self.browser.find_elements_by_name("edit")
        self.assertEqual(3, len(edit_elements))

        edit_dir_a = edit_elements[0]
        href = edit_dir_a.get_attribute("href")

        # go into directory's edit page
        edit_dir_a.click()
        self.assertEqual(href, self.browser.current_url)
        self.assertInBody("Edit directory")

        # verify that the name is pre-filled
        name_input = self.browser.find_element_by_name("name")
        self.assertEqual("a", name_input.get_attribute("value"))

        # change the name
        name_input.clear()
        name_input.send_keys("primary")
        self.browser.find_element_by_id("submit").click()

        self.assertEqual(self.custom_page_url, self.browser.current_url)
        self.assertInBody("primary")
