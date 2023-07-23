import requests
import fake_headers
import bs4
import re
import json


headers = fake_headers.Headers(browser='firefox', os='win')
headers_dict = headers.generate()
response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=headers_dict)
html = response.text
soup = bs4.BeautifulSoup(html, 'lxml')
main_div = soup.find('div', id='a11y-main-content')

result = {}
div_i = main_div.find_all('div', class_="vacancy-serp-item__layout")
for it in div_i:
    h3_name_a_tag = it.find('h3', class_="bloko-header-section-3")
    a_tag_vacancy = h3_name_a_tag.find('a')
    org_tag = it.find('div', class_="vacancy-serp-item-company")
    org_text = org_tag.find('div', class_="vacancy-serp-item__meta-info-company")
    org_name = org_text.find('a').text
    link = a_tag_vacancy['href']
    item_number = 0
    name = a_tag_vacancy.text
    cost_tag = it.find('span', class_="bloko-header-section-3")
    cost_min = 0
    cost_max = 0
    currency = ''
    city_text = ''
    if cost_tag is not None:
        cost_text = cost_tag.text
        if cost_text[:2] == 'от':
            cost_min = ''.join(re.findall(r'\S+', cost_text[2:].strip()))
            currency = cost_min[-1]
            cost_min = cost_min[:-1]
        elif cost_text[:2] == 'до':
            cost_max = ''.join(re.findall(r'\S+', cost_text[2:].strip()))
            currency = cost_max[-1]
            cost_max = cost_max[:-1]
        else:
            cost_min = cost_text[:cost_text.find('–')].strip()
            cost_min = ''.join(cost_min.split())
            cost_max = cost_text[cost_text.find('–')+1:-1].strip()
            cost_max = ''.join(cost_max.split())
            currency = cost_text[-1]
    sub_html = requests.get(link, headers=headers.generate()).text
    sub_soup = bs4.BeautifulSoup(sub_html, 'lxml')
    k_div = sub_soup.find('div', class_="bloko-tag-list")
    k_words = []
    if k_div is not None:
        ks_divs = k_div.find_all('div', class_="bloko-tag bloko-tag_inline")
        k_words = []
        for k in ks_divs:
            k_words.append(k.find('span').text)
    if 'Django' in k_words or 'Flask' in k_words:
        city_tag = sub_soup.find('div', class_="vacancy-company-redesigned")
        if city_tag is not None:
            city = city_tag.find('p')
            if city is not None:
                city_text = city.text
        item_number += 1
        result['item'+str(item_number)] = { 'link': link, 'Vacancy_name': name, 'org_name': org_name, 'cost': [cost_min, cost_max, currency], 'city': city_text}
print(result)

with open('res.json','w') as f:
    json.dump(result, f)