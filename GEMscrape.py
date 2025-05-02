from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time

# Setup
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Use new headless for stability
driver = webdriver.Chrome(service=Service(), options=options)

driver.get("https://gem.gov.in/userFaqs")
time.sleep(2)

faq_data = {}

# Get all tab buttons
tabs = driver.find_elements(By.CSS_SELECTOR, "ul.nav-tabs li a")

for index, tab in enumerate(tabs):
    category = tab.text.strip()

    # Click tab
    driver.execute_script("arguments[0].click();", tab)
    time.sleep(2)  # Wait for content to show

    # Get page content after tab becomes visible
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tab_panes = soup.select(".tab-content .tab-pane")

    # Grab the nth tab-pane assuming same order as tabs
    current_tab = tab_panes[index] if index < len(tab_panes) else None
    if not current_tab:
        continue

    faqs = current_tab.find_all("div", class_="panel panel-default")
    faq_list = []

    for faq in faqs:
        q_tag = faq.find("h4", class_="panel-title")
        a_tag = faq.find("div", class_="panel-body")
        if q_tag and a_tag:
            faq_list.append({
                "question": q_tag.get_text(strip=True),
                "answer": a_tag.get_text(strip=True)
            })

    faq_data[category] = faq_list

driver.quit()

# Convert to JSON
json_output = json.dumps(faq_data, indent=2, ensure_ascii=False)
print(json_output)

# Optional: Save to file
with open("gem_faqs.json", "w", encoding="utf-8") as f:
    f.write(json_output)
