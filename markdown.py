# encoding:utf-8

import re
import requests
import os

import plugins
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *


@plugins.register(
    name="dow_markdown",
    desire_priority=66,
    hidden=False,
    desc="优化markdown返回结果中的图片和网址链接。",
    version="0.1",
    author="Kubbo",
)
class dow_markdown(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_decorate_reply
            logger.info("[dow_markdown] inited.")
        except Exception as e:
            logger.warn("[dow_markdown] init failed, ignore.")
            raise e
    def on_decorate_reply(self, e_context: EventContext):
        if e_context["reply"].type != ReplyType.TEXT:
            return
        try:
            channel = e_context["channel"]
            context = e_context["context"]
            content = e_context["reply"].content.strip()
            # 避免图片无法下载时，重复调用插件导致没有响应的问题
            if content.startswith("[DOWNLOAD_ERROR]"):
                return
            if bool(re.search(r'\!\[[^\]]+\]\(?',content)):
                host = os.environ.get('DIFY_API_BASE', 'http://121.37.155.68:35801')
                image_path = re.search(r'!\[.*\]\((.*?)\)',reply.content).group(1)
                logger.info(f"提取到的数据==>host:{host},url:{image_path}")
                reply = Reply(ReplyType.IMAGE_URL, f"{host}{image_path}")
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            # 去掉每行结尾的Markdown链接中网址部分的小括号，避免微信误以为“)”是网址的一部分导致微信中无法打开该页面
            content_list = content.split('\n')
            new_content_list = [re.sub(r'\((https?://[^\s]+)\)$', r' \1', line) for line in content_list]
            if new_content_list != content_list:
                logger.info(f"[dow_markdown] parenthesis in the url has been removed, content={content}")
                reply = Reply(ReplyType.TEXT, '\n'.join(new_content_list).strip())
                e_context["reply"] = reply
        except Exception as e:
            logger.warn(f"[dow_markdown] on_decorate_reply failed, content={content}, error={e}")
        finally:
            e_context.action = EventAction.CONTINUE

    def decorate_markdown_image(self, content):
        # 完全匹配Coze画图的Markdown图片，coze.com对应ciciai.com，coze.cn对应coze.cn
        markdown_image_official = r"([\S\s]*)\!?\[(?P<image_name>.*)\]\((?P<image_url>https\:\/\/\S+?\.(ciciai\.com|coze\.cn)\/[\S]*\.png(\?[\S]*)?)\)([\S\s]*)"
        match_obj_official = re.fullmatch(markdown_image_official, content)
        if match_obj_official and match_obj_official.group('image_url'):
            image_name, image_url = match_obj_official.group('image_name'), match_obj_official.group('image_url')
            logger.info(f"[dow_markdown] markdown_image_official found, image_name={image_name}, image_url={image_url}")
            reply = Reply(ReplyType.IMAGE_URL, image_url)
            return [reply]
        # 完全匹配一张Markdown图片（格式：`![name](url)`）
        markdown_image_single = r"\!\[(?P<image_name>.*)\]\((?P<image_url>https?\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(:[0-9]{1,5})?(\/[\S]*)\.(jpg|jpeg|png|gif|bmp|webp)(\?[\S]*)?)\)"
        match_obj_single = re.fullmatch(markdown_image_single, content, re.DOTALL)
        if match_obj_single and match_obj_single.group('image_url'):
            image_name, image_url = match_obj_single.group('image_name'), match_obj_single.group('image_url')
            logger.info(f"[dow_markdown] markdown_image_single found, image_name={image_name}, image_url={image_url}")
            reply = Reply(ReplyType.IMAGE_URL, image_url)
            return [reply]
        # 匹配多张Markdown图片(格式：`url\n![Image](url)`)
        markdown_image_multi = r"(?P<image_url>https?\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(:[0-9]{1,5})?(\/[\S]*)\.(jpg|jpeg|png|gif|bmp|webp)(\?[\S]*)?)\n*\!\[Image\]\((?P=image_url)\)"
        match_iter_multi = re.finditer(markdown_image_multi, content)
        replies = []
        for match in match_iter_multi:
            image_url = match.group('image_url')
            logger.info(f"[dow_markdown] markdown_image_multi found, image_url={image_url}")
            reply = Reply(ReplyType.IMAGE_URL, image_url)
            replies.append(reply)
        if replies:
            return replies
        if content.startswith('![') and 'http' in content and any(img in content for img in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']):
            logger.info(f"[dow_markdown] it seems markdown image in the content but not matched, content={content}.")

    def get_help_text(self, **kwargs):
        return "优化返回结果中的图片和网址链接。"
