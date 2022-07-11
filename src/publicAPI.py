from PicImageSearch import SauceNAO,Network
from utils import config
from pixivpy_async import *
import re

from .dao import verifyDao

sauceNAO_token = config['sauceNAO']['token']
sauceNAO_proxy_on = config['sauceNAO']['proxy_on']
pixiv_proxy_on = config['pixiv']['proxy_on']
pixiv_bypass = config['pixiv']['bypass_SNI']
pixiv_refresh_token = config['pixiv']['refresh_token']
pixiv_username = config['pixiv']['username']
pixiv_password = config['pixiv']['password']
proxy = config['proxies']['proxy']

#获取图片pixiv_id
async def get_pixiv_id(url):
    """
    url: 待搜索图片url
    从sauceNAO上搜索图片，返回P站ID和文件名
    """
    try:
        pixiv_id,sauceNAO_proxy = 0,None
        if sauceNAO_proxy_on:
            sauceNAO_proxy = proxy
        async with Network(proxies = sauceNAO_proxy) as client:
            saucenao = SauceNAO(api_key=sauceNAO_token, client=client, minsim = 60)
            res = await saucenao.search()
        if res:
            for raw in res.raw:
                pixiv_id = raw.pixiv_id     
                index_name = raw.index_name
                if pixiv_id:
                    return pixiv_id,index_name
                else:
                    return 0,''
        else:
            return 0,''
    except Exception as e:
        print(e)
        return 0,''
    
#获取图片pixiv_tag和原图urla
async def get_pixiv_tag_url(pixiv_id,page):
    """
    pixiv_id: P站作品ID
    page: P站作品页码
    返回TAG,中文TAG，是否R18，P站大图链接
    """
    try:
        if sauceNAO_proxy_on:
            pixiv_proxy = proxy
            async with PixivClient(proxy = pixiv_proxy) as client:
                aapi = AppPixivAPI(client=client,proxy = pixiv_proxy)
            if pixiv_proxy_on:
                await aapi.login(refresh_token=pixiv_refresh_token)
            elif pixiv_username and pixiv_password:
                await aapi.login(pixiv_username, pixiv_password)
            aapi.set_accept_language('zh-cn')
            json_result = aapi.illust_detail(pixiv_id)
            if not json_result.illust.title:
                return '','',0,''
            page_count = json_result.illust.page_count
            illust = json_result.illust.tags
            r18 = 0
            pixiv_tag = ''
            pixiv_tag_t = ''
            pixiv_img_url =''
            if illust[0]['name'] == 'R-18':
                r18 = 1
            for i in illust:
                pixiv_tag = pixiv_tag.strip()+ " "+ str(i['name']).strip('R-18')
                pixiv_tag_t = pixiv_tag_t.strip() + " "+ str(i['translated_name']).strip('None') #拼接字符串 处理带引号sql
            pixiv_tag = pixiv_tag.strip()
            pixiv_tag_t = pixiv_tag_t.strip()
            if page_count == 1:
                pixiv_img_url=json_result.illust.meta_single_page['original_image_url']
            else:
                pixiv_img_url=json_result.illust.meta_pages[int(page)]['image_urls']['original']
            return pixiv_tag,pixiv_tag_t,r18,pixiv_img_url
        else:
            return '','',0,''
    except Exception as e:
        return '','',0,''


#图片检测相似度，自动获取TAG
async def verify(id,url):
    """
    id:色图ID
    url:待搜索图片url
    返回：色图ID,审核状态,P站ID,待搜索图片url
    """
    pixiv_id,index_name=get_pixiv_id(url)
    if not pixiv_id:
        verify = verifyDao().update_verify_stats(id,1)
    else:
        page = re.search(r'_p(\d+)',index_name,re.X)
        pixiv_tag,pixiv_tag_t,r18,pixiv_url=get_pixiv_tag_url(pixiv_id,page.group(1))
        if not pixiv_tag:
            verify = verifyDao().update_verify_stats(id,1)
        else:
            verify = verifyDao().update_verify_info(id, pixiv_id ,pixiv_tag ,pixiv_tag_t ,r18 ,pixiv_url)
    return id,verify,pixiv_id,url