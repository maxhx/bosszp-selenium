import datetime
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dbutils import DBUtils

# Set up the browser options
driver_path = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe'

# 创建 Edge Options 对象
edge_options = Options()
edge_options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\miedge.exe"  # 替换为你的实际路径

# 在这里可以设置其他选项，例如无头模式
# edge_options.add_argument('--headless')

# 创建 Service 对象
edge_service = Service(executable_path=driver_path)

browser = webdriver.Edge(service=edge_service, options=edge_options)

# Define the database connection
db = DBUtils('localhost', 'root', '123456', 'spider_db')

# Open the job search page
url = "https://we.51job.com/pc/search?jobArea=000000&keyword=django&searchType=2&keywordType="
browser.get(url)

# Define the pagination parameters
category_pages = 10  # Number of pages for categories
job_pages = 10  # Number of pages for job listings

for category_page in range(1, category_pages + 1):
    try:
        # Get the list of job categories
        categories = browser.find_elements(By.XPATH, '//div[@class="category-list"]/ul/li/a')
        
        # Iterate over each category
        for category in categories:
            # Get the category name and URL
            category_name = category.text.strip()
            category_url = category.get_attribute('href')
            
            # Open the category page
            browser.get(category_url)
            
            # Scroll down to the end of the page
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Get the list of job listings
            job_listings = browser.find_elements(By.XPATH, '//div[@class="result-list"]/ul/li')
            
            # Iterate over each job listing
            for job_listing in job_listings:
                # Get the job details
                title = job_listing.find_element(By.XPATH, './div[@class="job-info"]/h3/a/span').text.strip()
                location = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[1]').text.strip()
                company = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[2]').text.strip()
                industry = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[3]').text.strip()
                finance = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[4]').text.strip()
                scale = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[5]').text.strip()
                welfare = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[6]').text.strip()
                salary_range = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[7]').text.strip()
                experience = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[8]').text.strip()
                education = job_listing.find_element(By.XPATH, './div[@class="job-info"]/p/span[9]').text.strip()
                skills = ','.join([skill.text.strip() for skill in job_listing.find_elements(By.XPATH, './div[@class="job-requirement"]/ul/li')])
                
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                
                # Extract additional information from the HTML content
                
                # Save the data to the database
                db.execute("insert into job_info(category_name, title, location, company, industry, finance, scale, welfare, salary_range, experience, education, skills) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (category_name, title, location, company, industry, finance, scale, welfare, salary_range, experience))

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
        continue

    break

# Close the browser window
browser.quit()

# Commit the changes and close the database connection
db.commit()
db.close()