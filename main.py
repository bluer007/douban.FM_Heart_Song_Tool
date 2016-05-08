#coding:utf-8
import urllib
import urllib2
import cookielib
import os
import json
import time
import gzip
import sys
from StringIO import StringIO

def Clean():
    '''清理cookie和验证码图片'''
    DeleteFile(captchaFile)
    DeleteFile(cookiePath)

def GetDesktopPath():
    '''获取当前用户桌面路径'''
    return os.path.join(os.path.expanduser("~"), 'Desktop')

def DeleteFile(path):
    '''删除文件'''
    if os.path.exists(path):
        os.remove(path)

def SaveImg(path, buf, mode):
    '''保存图片(验证码图片)'''
    f = file(path, mode)
    f.write(buf)
    f.close()

def SaveFile(path, buf, mode):
    '''保存文件(歌曲列表文件)'''
    f = file(path, mode)
    f.write(buf.encode('utf-8','ignore'))
    f.close()

cookiePath = GetDesktopPath() + '/cookie.txt'
captchaFile = GetDesktopPath() + '/captcha.jpg'
songFile = GetDesktopPath() + u'/红心歌曲.txt'

captchaURL = r'http://douban.fm/j/new_captcha'
likeURL = ur'http://douban.fm/j/play_record?'
loginURL = r'http://douban.fm/j/login'          #   http://douban.fm/j/misc/login_form


#修改默认编码, 避免保存文件时乱码
reload(sys)
sys.setdefaultencoding('utf-8')


#声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
cookie = cookielib.MozillaCookieJar(cookiePath)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

loginHeaders = {
    'Accept': r'*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Host': 'douban.fm',
    'Referer': r'http://douban.fm/',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

print '\n------ 欢迎使用 豆瓣FM红心歌曲获取器v2.0 ------\n\n准备登录帐号.....'.decode('utf-8','ignore')
#刷新验证码
result = opener.open(captchaURL)
cookie.save(ignore_discard=True, ignore_expires=True)
print '获取验证码.....'.decode('utf-8', 'ignore')
captchaStr = result.read()
print ('验证码ID: '+captchaStr).decode('utf-8', 'ignore')    #captchaStr相当于验证码图片的ID号

#获取验证码图片
captchaStr = captchaStr[1:-1]
captchaPicURL = r'http://douban.fm/misc/captcha?size=m&id=' + captchaStr
result = opener.open(captchaPicURL)
cookie.save(ignore_discard=True, ignore_expires=True)
DeleteFile(captchaFile)
SaveImg(captchaFile, result.read(), 'wb')


#发送登录信息, 开始登陆
loginedHeaders = {
    'Accept': r'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Host': 'douban.fm',
    'Origin': r'http://douban.fm',
    'Referer': r'http://douban.fm/',
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

time.sleep(1)

os.system('start "" "%s"' % captchaFile)
captchaAnswer = raw_input("\n请输入打开的图片的验证码:".decode('utf-8').encode('gbk'))
username = raw_input("请输入用户名/邮箱:".decode('utf-8').encode('gbk'))
password = raw_input("请输入密码:".decode('utf-8').encode('gbk'))

postdata = urllib.urlencode({
    'source': 'radio',
    'alias': username,
    'form_password': password,
    'captcha_solution': captchaAnswer,
    'captcha_id': captchaStr,
    'task': 'sync_channel_list'
		})

request = urllib2.Request(loginURL, postdata, loginedHeaders)
result = opener.open(request)
#保存cookie到cookie.txt中
cookie.save(ignore_discard=True, ignore_expires=True)
userInfo = result.read()
#print userInfo.decode('utf-8')

#输出用户基本信息
userJson = json.loads(userInfo)
if userJson['r'] == 1:
    print (u"\n\n帐号认证错误: %s\n请重新运行程序试试吧\n" % (userJson['err_msg'])).decode('utf-8')
    Clean()
    os.system("pause")
    exit(-1)


print '\n\n帐号认证成功----------'.decode('utf-8')
print (u'欢迎你,%s' % userJson['user_info']['name']).decode('utf-8')
print (u'红心歌曲数目: %d' % userJson['user_info']['play_record']['liked']).decode('utf-8')
print (u'播放歌曲总数目: %d' % userJson['user_info']['play_record']['played']).decode('utf-8')
print (u'不再播放歌曲数目: %d' % userJson['user_info']['play_record']['banned']).decode('utf-8')
DeleteFile(songFile)
SaveFile(songFile, u'------------ 欢迎使用 豆瓣FM红心歌曲获取器v2.0 ------------\n\n欢迎你, %s\n' % userJson['user_info']['name'], 'a')
SaveFile(songFile, u'红心歌曲数目: %d\n' % userJson['user_info']['play_record']['liked'], 'a')
SaveFile(songFile, u'播放歌曲总数目: %d\n' % userJson['user_info']['play_record']['played'], 'a')
SaveFile(songFile, u'不再播放歌曲数目: %d\n\n\n\n' % userJson['user_info']['play_record']['banned'], 'a')


#检索红心歌曲
print '\n\n开始检索红心歌曲'.decode('utf-8')
def ListLikeSong(startNum):
    '''发送红心歌曲的链接请求函数'''
    bidNum = 0
    likeParam = (u'ck=%s' % userJson['user_info']['ck'] + u'&spbid=%3A%3A')
    for item in cookie:
        if item.name == 'bid':
            bidNum += 1
            if bidNum == 2:
                likeParam += item.value
                break
    #    print 'Name = '+item.name
    #    print 'Value = '+item.value
    tmp_likeURL = likeURL + likeParam + u'&type=liked&start=' + unicode(startNum)
    global request
    request = urllib2.Request(tmp_likeURL, data=None, headers=loginedHeaders)
    global result
    result = opener.open(request)
    cookie.save(ignore_discard=True, ignore_expires=True)
    if result.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(result.read())
        f = gzip.GzipFile(fileobj=buf)
        m_songJson = f.read()
    else:
        m_songJson = result.read()
    return json.loads(m_songJson)

def is_chinese(uchar):
    """判断一个unicode是否是汉字(包括日文韩语等)"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

def fill_text_to_print_width(text, width):
    '''对text填充空格使一定宽度函数'''
    stext = str(text)
    utext = stext.decode("utf-8",'ignore')
    cn_count = 0
    for u in utext:
        if is_chinese(u):
            cn_count += 1
    str2 = stext + " " * (width - cn_count - len(utext))
    return str2


def print_table_line(title_config_pairs):
    '''使中英文对齐输出函数'''
    fmt = "".join((["{}"] * len(title_config_pairs)))
    format_line = fmt.format(*map(lambda x: fill_text_to_print_width(x[0], x[1]), title_config_pairs))
    return format_line

songNum = 0
songStart = 0
SaveFile(songFile, u'红心歌曲列表:\n\n', 'a')
line = print_table_line((
    (u'编号', 10),
    (u'歌曲', 60),
    (u"歌手", 60)
))
SaveFile(songFile, line + u'\n', 'a')

while songStart < userJson['user_info']['play_record']['liked']:
    songJson = ListLikeSong(songStart)
    for num in range(len(songJson['songs'])):
        songNum += 1
        line = print_table_line((
            (u'%d.' % songNum, 10),
            (songJson['songs'][num]['title'] , 60),
            (songJson['songs'][num]['artist'], 60)
        ))
        #line = unicode(songNum) + u'.       ' + songJson['songs'][num]['title'] + u'       歌手: ' + songJson['songs'][num]['artist']
        print line.encode('gbk','ignore')
        SaveFile(songFile, line + u'\n', 'a')
    songStart += songJson['per_page']

#输出总结信息
if songNum == userJson['user_info']['play_record']['liked']:
    print ('\n成功获取所有红心歌曲,共 %d 首. 已将"红心歌曲.txt"保存在桌面.\n\n欢迎再次使用本程序~~~88~~' % songNum).decode('utf-8','ignore')
else:
    print ('\n成功获取 %d 首红心歌曲,失败 %d 首. 已经"红心歌曲.txt"保存在桌面.\n\n欢迎再次使用本程序~~~88~~' % (songNum, userJson['user_info']['play_record']['liked'] - songNum)).decode('utf-8','ignore')

Clean()
os.system("pause")
exit()












