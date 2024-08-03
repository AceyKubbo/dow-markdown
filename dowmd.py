# encoding:utf-8

import re
import requests
import os

import plugins
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from lib import itchat

@plugins.register(
    name="dow_markdown",
    desire_priority=66,
    desc="优化markdown返回结果中的图片和网址链接。",
    version="0.2",
    author="Kubbo",
)
class dow_markdown(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_DECORATE_REPLY] = self.on_decorate_reply
            logger.info("[dow_markdown] inited.")
        except Exception as e:
            logger.warn("[dow_markdown] init failed, ignore.")
            raise e
    def on_handle_context(self,e_content:EventContext):
        try:
            send_msg = e_content["context"]
            if send_msg["type"] == ReplyType.TEXT:
                if any(word in send_msg["content"] for word in ["画"]):
                    receiver = send_msg.get("receiver")
                    itchat.send("我正在绘画中,可能需要多等待一会,请稍后...",toUserName=receiver)
                    e_content.action = EventAction.CONTINUE
        finally:
            e_content.action = EventAction.CONTINUE
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
            has_md = re.search(r'\!\[[^\]]+\]\(?',content)
            if has_md:
                host = os.environ.get('DIFY_API_BASE', 'http://121.37.155.68:35801')
                image_path = re.search(r'!\[.*\]\((.*?)\)',content).group(1)
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
    def get_help_text(self, **kwargs):
        return "优化返回结果中的图片和网址链接。"
