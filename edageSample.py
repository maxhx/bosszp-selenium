from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# 指定 Microsoft Edge WebDriver 路径
driver_path = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe'

# 创建 Edge Options 对象，并指定 Microsoft Edge 浏览器的路径
edge_options = Options()
edge_options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\miedge.exe"  # 替换为你的实际路径

# 创建 Service 对象
edge_service = Service(executable_path=driver_path)

# 创建 Edge WebDriver 对象
driver = webdriver.Edge(service=edge_service, options=edge_options)

# 访问一个网站以测试
driver.get('https://www.example.com')
print(driver.title)

# 关闭 WebDriver
driver.quit()
