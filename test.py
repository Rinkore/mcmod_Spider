import json
import os
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
from random import randint


ua = UserAgent()
random_ua = ua.random
headers = {
    'User-Agent': random_ua,
}

def get_mod_detail(inner_url):
    # time.sleep(randint(0, 10))
    response = requests.get('https://www.mcmod.cn/' + inner_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    mod_data = {}
    '''
    获取总下载量
    '''
    infos = soup.find('div', class_='infos')
    infos_divs = infos.find_all('div')
    for div in infos_divs:
        if div['title'].isdigit():
            total_views = int(div['title'])
            mod_data['total_views'] = total_views
            break
    '''
    获取运行环境
    '''
    sidebar_infos = soup.find('div', class_='class-info') \
        .find('div', class_='class-info-left') \
        .find_all('li', class_='col-lg-4')
    for li in sidebar_infos:
        text = li.get_text().strip()
        if ':' in text:
            key, value = text.split(':')
            mod_data[key] = value.strip()
    '''
    获取评分
    '''
    votes = soup.find('div', class_='class-card').find('div', class_='text-block').find_all('span')
    mod_data['red'] = votes[0].get_text()
    mod_data['black'] = votes[1].get_text()
    rate = soup.find('div', id='class-rating').get('data-original-title').split('<br/>')
    mod_data['rate'] = rate

    '''
    获取支持的mc版本
    '''
    # 找出所有<li>标签
    version_lis = soup.find('li', class_='col-lg-12 mcver').find_all('li')
    category = None
    for version_li in version_lis:
        text = version_li.get_text().strip()
        if text.endswith(':'):
            category = text
        a_tag = version_li.find('a')
        if a_tag:
            version = a_tag.get_text()
            if category:
                mod_data.setdefault(category, []).append(version)
    return json.dumps(mod_data, ensure_ascii=False)


def get_page(page):
    # time.sleep(randint(0, 1))
    url = 'https://www.mcmod.cn/modlist.html?sort=createtime&page=' + str(page)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    mod_blocks = soup.find_all('div', class_='modlist-block')
    mods = []
    for mod_block in mod_blocks:
        mod_data = {}
        cover_url = mod_block.find('img').get('src')
        inner_url = mod_block.find('div', class_='title').find('a').get('href')
        name = mod_block.find('p', class_='name').text.strip()
        ename = mod_block.find('p', class_='ename').text.strip()
        intro_div = mod_block.find('div', class_='intro')
        if intro_div:
            intro = intro_div.text.strip()
        else:
            intro = ''
        mod_data['name'] = name
        mod_data['ename'] = ename
        mod_data['intro'] = intro
        mod_data['inner_url'] = inner_url
        mod_data['cover'] = cover_url
        # 获取子项目
        items_table_hover = mod_block.find_all('div', class_='item-table-hover')
        items = []
        for item_table_hover in items_table_hover:
            item_data = {}
            item_data['img_alt'] = item_table_hover.find('img').get('alt')
            item_data['img_src'] = item_table_hover.find('img').get('src')
            item_data['href'] = item_table_hover.find('a').get('href')
            items.append(item_data)
        mod_data['items'] = items
        # 获取mod详情
        # 调用get_mod_detail获取详情JSON
        detail_json = get_mod_detail(inner_url)

        # 解析为Python字典
        detail_data = json.loads(detail_json)

        # 直接将detail_data的元素追加到mod_data
        mod_data.update(detail_data)
        mods.append(mod_data)
        # print(mod_data)
        mod_name = mod_data['inner_url'][7:-5]
        print(mod_name)
        with open('result/{}.json'.format(mod_name), 'w', encoding='utf-8') as f:
            json_str = json.dumps(mod_data, ensure_ascii=False)
            f.write(json_str)
    # result = {}
    # result['mods'] = mods
    # return json.dumps(result, ensure_ascii=False)


def get_last_page(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    page_links = soup.find_all('a', class_='page-link')

    last_page = 0
    for link in page_links:
        page_num = link.get('data-page')
        if page_num:
            last_page = max(last_page, int(page_num))
    return last_page


def main():
    last_page = get_last_page(first_page)

    # 并发爬取所有页
    pool = Pool(16)
    pool.map(get_page, list(range(1, last_page + 1)))
    pool.close()
    pool.join()

# def main():
#     last_page = get_last_page(first_page)
#
#     # 顺序爬取所有页
#     for page in range(170, last_page + 1):
#         get_page(page)


if __name__ == '__main__':
    if not os.path.exists('result'):
        os.mkdir('result')
    first_page = 'https://www.mcmod.cn/modlist.html?sort=createtime&page=1'
    # result = get_page(309)
    main()