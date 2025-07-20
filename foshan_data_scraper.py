
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# 初始化浏览器
options = Options()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

# 目标网址
url = "http://jy.ggzy.foshan.gov.cn:3680/TPBank/newweb/framehtml/onlineTradex/index.html"
driver.get(url)

# 等待加载并点击“历史交易”
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "历史交易")]'))
).click()

# 等待 iframe 加载
time.sleep(3)
iframe = driver.find_element(By.ID, "myiframe")
driver.switch_to.frame(iframe)

# 存储数据
data = []

# 翻页数
MAX_PAGES = 5

for page in range(MAX_PAGES):
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, '//tr[contains(@class, "tr_line")]')
    
    for i in range(len(rows)):
        try:
            rows = driver.find_elements(By.XPATH, '//tr[contains(@class, "tr_line")]')
            status = rows[i].find_elements(By.TAG_NAME, 'td')[-1].text.strip()
            if status not in ['已成交', '竞价结束']:
                continue

            rows[i].click()
            time.sleep(2)

            def get_value(label):
                try:
                    el = driver.find_element(By.XPATH, f'//td[contains(text(), "{label}")]/following-sibling::td[1]')
                    return el.text.strip()
                except:
                    return ""

            record = {
                '成交时间': get_value('成交时间'),
                '竞得人': get_value('竞得人'),
                '交易土地面积': get_value('交易土地面积'),
                '成交地价': get_value('成交地价'),
                '地块位置': get_value('地块位置'),
                '土地实际用途': get_value('土地实际用途'),
                '状态': status
            }
            data.append(record)

            driver.back()
            driver.switch_to.frame("myiframe")
            time.sleep(2)

        except Exception as e:
            print("异常跳过:", e)
            driver.switch_to.frame("myiframe")
            continue

    try:
        next_btn = driver.find_element(By.LINK_TEXT, '下一页')
        next_btn.click()
    except:
        print("已到最后一页")
        break

df = pd.DataFrame(data)
df.to_excel("佛山历史交易数据.xlsx", index=False)
print("✅ 数据采集完成，共采集：", len(data), "条记录。")
driver.quit()
