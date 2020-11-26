import os
import re
import sys
import time
import requests
import logging
import random
import hashlib
from lxml import etree


SAVE_PATH = r''
if len(SAVE_PATH) == 0:
    SAVE_PATH = os.getcwd()


logger = logging.getLogger('spider')
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class JSBit32Num(int):

    """
    构造一个类似于 javascript 里面位运算的 32 位数
    当使用位操作时，如果数溢出将自动去除掉溢出部分
    右移和减法等操作因为不涉及和没有实际用过不知道结果
    是什么样子的，不实现了 ^_^
    """

    def check(self, num):
        if num > 0xFFFFFFFF:
            num = num & 0xFFFFFFFF
        return num

    def __lshift__(self, other):
        value = int.__lshift__(self, other)
        return self.check(value)

    def __add__(self, other):
        value = int.__add__(self, other)
        return self.check(value)

    def __radd__(self, other):
        value = int.__radd__(self, other)
        return self.check(value)


class QQSpaceSpider:

    def __init__(self, qq):

        self.qq = qq
        self.s = requests.session()
        self.set_headers()
        # self.set_cookies()
        self.p_skey = self.get_p_skey()
        self.g_tk = self.get_gtk(self.p_skey)

    def download_picture(self, target_qq, include_list=None, exclude_list=None, exclude_key=None, name_mode=1):

        if len(target_qq) == 0:
            print('Please set the target_qq')
            sys.exit()
        res = self.s.get(url='https://user.qzone.qq.com/{}'.format(target_qq))
        title = self.get_title(res)
        print(title)
        if target_qq not in title:
            print("Can not get the right page, please update the cookie.")
            sys.exit()
        time.sleep(1)

        # picture entrance
        url = 'https://user.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/fcg_list_album_v3?'
        params = {'appid': '4',
                  'callback': 'shine4_Callback',
                  'callbackFun': 'shine4',
                  'filter': '1',
                  'format': 'json',     # the default is 'jsoup', set to 'json' to get the json data
                  'g_tk': self.g_tk,
                  'handset': '4',
                  'hostUin': target_qq,
                  'idcNum': '4',
                  'inCharset': 'utf-8',
                  'mode': '2',
                  'needUserInfo': '1',
                  'notice': '0',
                  'outCharset': 'utf-8',
                  'pageNum': '10000',
                  'pageNumModeClass': '15',
                  'pageNumModeSort': '40',
                  'pageStart': '0',         # set 0 to get all the picture data
                  'plat': 'qzone',
                  'sortOrder': '0',
                  'source': 'qzone',
                  't': '970495431',
                  'uin': self.qq}
        res = self.s.get(url, params=params)
        # self.res = res
        data = res.json()
        data_list = data['data']['albumList']
        print('总共有 {} 组图片，现在开始遍历...'.format(len(data_list)))
        for index, each in enumerate(data_list):
            title = each['name']
            topic_id = each['id']
            total = each['total']
            createtime = each['createtime']
            modifytime = each['modifytime']
            question = each.get('question', None)
            print('-' * 30)
            print('第 {}/{} 组：{}'.format(index + 1, len(data_list), title))
            # if question is not None:
            #     print('{} 设置有问题，已略过。'.format(title))
            #     continue
            # self.get_pic_url_list(target_qq, topic_id)

            if include_list:
                if title not in include_list:
                    continue
            elif exclude_list:
                if title in exclude_list:
                    continue
            elif exclude_key:
                if exclude_key in title:
                    continue
            # self.get_pic_url_list(target_qq, topic_id, name_mode)
            # time.sleep(1)

    def get_pic_url_list(self, target_qq, topic_id, name_mode=1):
        url = 'https://h5.qzone.qq.com/proxy/domain/photo.qzone.qq.com/fcgi-bin/cgi_list_photo?'
        params = {'_': '1606293090755',
                  'answer': '',
                  'appid': '4',
                  'batchId': '',
                  'callback': 'shine0_Callback',
                  'callbackFun': 'shine0',
                  'format': 'json',
                  'g_tk': self.g_tk,
                  'hostUin': target_qq,
                  'idcNum': '4',
                  'inCharset': 'utf-8',
                  'json_esc': '1',
                  'mode': '0',
                  'noTopic': '0',
                  'notice': '0',
                  'outCharset': 'utf-8',
                  'outstyle': 'json',
                  'pageNum': '10000',      # 正常情况是 30 ，但是为了一次性获得所有数据，我设置了一个比较大的值
                  'pageStart': '0',
                  'plat': 'qzone',
                  'question': '',
                  'singleurl': '1',
                  'skipCmtCount': '0',
                  'source': 'qzone',
                  't': '210213950',
                  'topicId': topic_id,
                  'uin': self.qq}
        res = self.s.get(url, params=params)
        data = res.json()
        photo_list = data['data']['photoList']
        topic = data['data']['topic']

        name = topic['name']
        topic_modifytime = topic['modifytime']

        download_url_list = []

        previous_upload_time = ''
        flag = 1
        for detail in photo_list:
            is_video = detail['is_video']
            modifytime = detail['modifytime']
            origin_url = detail['origin_url']
            uploadtime = detail['uploadtime']
            url = detail['url']

            if not is_video:
                head = ''.join(re.findall(r'\d', uploadtime))
                tail = 'jpg'
                if name_mode == 1:
                    if previous_upload_time == uploadtime:
                        head = head + '-{}'.format(flag)
                        flag += 1
                    else:
                        flag = 1
                else:
                    print('Please set the right name mode.')
                    sys.exit()
                picture_name = '{}.{}'.format(head, tail)
            else:
                print(is_video)
                print('这个是一个视频，目前跳过下载这部分。')
                continue

            if len(origin_url) > 0:
                download_url_list.append(
                    (picture_name, origin_url))
            else:
                download_url_list.append((picture_name, url))

            previous_upload_time = uploadtime

        total = len(photo_list)
        print('总共有 {} 张图片，现在开始下载...'.format(total))

        name = self.format_directory_name(name)
        picture_dir = os.path.join(SAVE_PATH, target_qq, name)
        if not os.path.exists(picture_dir):
            os.makedirs(picture_dir)

        existed_pic_num = len(os.listdir(picture_dir))
        if existed_pic_num == total:
            print('目标文件夹下存在 {} 张图片，图片已经下载完成。'.format(existed_pic_num))
            return

        for index, pic_data in enumerate(download_url_list):
            picture_name, url = pic_data[0], pic_data[1]
            picture_path = os.path.join(picture_dir, picture_name)
            index = index + 1
            # print('Download {}...'.format(url))
            if os.path.exists(picture_path):
                print('{} already exists.'.format(picture_path))
                continue
            # print('Download {}...'.format(url))
            t1 = time.time()
            res = self.s.get(url)
            if not self.check_pciture_completeness(res):
                print('The picture is not completely.')
                continue
            with open(picture_path, 'wb')as fl:
                fl.write(res.content)
            # print(
            #     '{} save successfully[{}/{}]'.format(picture_path, index, total))
            time.sleep(random.uniform(2.7, 3.7))
            t2 = time.time()
            print(
                '{} save successfully[{}/{}] cost {} s'.format(picture_path, index, total, t2 - t1))

    def check_cookie(self):
        res = self.s.get('https://user.qzone.qq.com/{}'.format(self.qq))
        title = self.get_title(res)
        print(title)
        time.sleep(1)
        if self.qq not in title:
            print('The cookie has expired, please update cookie at first.')
            sys.exit()

    def get_p_skey(self):
        # get p_skey form the cookie
        p_skey = re.findall(r'p_skey=(.{44})', self.s.headers['cookie'])
        if len(p_skey) == 1:
            return p_skey[0]
        else:
            print("Can't get p_skey, please update the headers.txt")
            sys.exit()

    def get_gtk(self, p_skey):
        # calculate g_tk from p_skey
        flag = JSBit32Num(5381)
        for letter in p_skey:
            flag += (flag << 5) + ord(letter)
        return flag & 0x7fffffff

    def set_headers(self):
        # headers = self.format_headers('headers.txt')
        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9',
                   'cache-control': 'max-age=0',
                   'referer': 'https://i.qq.com/',
                   'sec-fetch-dest': 'document',
                   'sec-fetch-mode': 'navigate',
                   'sec-fetch-site': 'same-site',
                   'sec-fetch-user': '?1',
                   'upgrade-insecure-requests': '1',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'
                   }
        self.s.headers.update(headers)
        with open('cookies.txt')as fl:
            cookie = fl.read().strip()
        self.s.headers['cookie'] = cookie

    def set_cookies(self):
        cookies_dict = self.format_cookies('cookies.txt')
        cookies = requests.utils.cookiejar_from_dict(cookies_dict)
        self.s.cookies = cookies

    def format_headers(self, filename):
        headers = {}
        with open(filename) as fl:
            for line in fl:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key] = value.strip()
        return headers

    def format_cookies(self, filename):
        cookies = {}
        with open(filename) as fl:
            data = fl.read().strip()
        for line in data.split(';'):
            head, tail = line.strip().split('=', 1)
            cookies[head.strip()] = tail.strip()
        return cookies

    def format_directory_name(self, directory_name):

        if directory_name is not None:
            directory_name = directory_name.strip()
            flag_list = ['/', '\\', ':', '*', '"', '<', '>', '|', '?']
            for line in flag_list:
                if line in directory_name:
                    directory_name = directory_name.replace(line, '')
        return directory_name

    def save_source_code(self, res):
        with open('source.html', 'w', encoding='utf-8') as fl:
            fl.write(res.text)

    def get_title(self, res):
        res.encoding = 'utf-8'
        response = etree.HTML(res.text)
        return response.xpath('//title/text()')[0]

    def check_pciture_completeness(self, picture_res):

        try:
            theoretical_content_length = picture_res.headers['Content-Length']
        except KeyError:
            print(picture_res.headers.items())
            print(
                "Can't get the content-length, some website limit the spider when the spider too fast.")
            print('Please slow down your spider, maybe it will be ok.')
            return False
        actual_content_length = str(len(picture_res.content))
        if theoretical_content_length == actual_content_length:
            return True
        else:
            return False

if __name__ == '__main__':

    # the qq of cookies
    spider = QQSpaceSpider(qq)
    # target qq to download pictures
    spider.download_picture(target_qq)
