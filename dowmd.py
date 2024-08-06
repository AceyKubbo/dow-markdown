# encoding:utf-8

import re

import plugins
from bridge.reply import Reply, ReplyType
from lib import itchat
from plugins import *
from config import conf


@plugins.register(
    name="dow_markdown",
    desire_priority=66,
    desc="优化markdown返回结果中的图片和网址链接。",
    version="0.5",
    author="Kubbo",
    hidden=False
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

    def on_handle_context(self, e_context: EventContext):
        send_msg = e_context["context"]
        try:
            text = send_msg["content"]
            if any(word in send_msg["content"] for word in ["画", ".sd"]):
                receiver = send_msg.get("receiver")
                itchat.send("我正在绘画中,可能需要多等待一会,请稍后...", toUserName=receiver)
                logger.info("[WX] sendMsg={}, receiver={}".format(text, receiver))
                e_context.action = EventAction.BREAK_PASS
        except Exception as e:
            text = send_msg["content"]
            logger.warn(f"[dow_markdown] on_handle_context failed, content={text}, error={e}")
        finally:
            e_context.action = EventAction.CONTINUE

    def on_decorate_reply(self, e_context: EventContext):
        if e_context["reply"].type != ReplyType.TEXT:
            return
        logger.info("[on_decorate_reply] yooooooooooooooooo")
        try:
            content = e_context["reply"].content.strip()
            # 避免图片无法下载时，重复调用插件导致没有响应的问题
            if content.startswith("[DOWNLOAD_ERROR]"):
                return
            content_arr = [m for m in content.split("<br>") if m.strip()]
            if len(content_arr) > 0:
                for index, msg in enumerate(content_arr):
                    self.handle_send(msg, e_context, index == len(content_arr) - 1)
        except Exception as e:
            logger.warn(f"[dow_markdown] on_decorate_reply failed, error={e}")
        finally:
            e_context.action = EventAction.CONTINUE

    def get_help_text(self, **kwargs):
        return "优化返回结果中的图片和网址链接。"

    def handle_send(self, content, e_context, is_last):
        host = os.environ.get('DIFY_API_BASE', '')
        if host.endswith('/v1'):
            host = host[:-3]
        if 'coze' == conf().get('model'):
            host = "https://s.coze.cn/t/"
        parts = re.split(r'\!\[[^\]]+\]\(?', content)
        parts = [p for p in parts if p.strip()]
        channel = e_context["channel"]
        context = e_context["context"]
        logger.info("[handle_send] parts={}".format(parts))
        if len(parts) > 0:
            for index, part in enumerate(parts):
                reply = Reply(content=part.strip(), type=ReplyType.TEXT)
                if re.search(r"\.(gif|jpg|png|jpeg|webp)", part):
                    reply.type = ReplyType.IMAGE_URL
                    reply.content = self.extract_url(part.strip(), host)
                elif re.search(r"\.(mp4)", part):
                    reply.type = ReplyType.VIDEO_URL
                    reply.content = self.extract_url(part.strip(), host)
                if index == len(parts) - 1 and is_last:
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                else:
                    channel.send(reply, context)

    def extract_url(self, text, host):
        text = text.strip()
        if text.endswith(")"):
            text = text[:-1]
        if not text.startswith('http'):
            if text.startswith('/t/') and 'coze' == conf().get('model'):
                text = text[3:]
            text = host + text
        return text
