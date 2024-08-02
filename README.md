一款用来适配Dify的chatbot的返回的markdown格式返回的消息处理

+ 提取Dify返回的Markdown图片链接中的网址，并修改ReplyType为IMAGE_URL，以便DoW自动下载Markdown链接中的图片；
+ 提取Dify返回的包含 https://s.coze.cn/t/xxx 网址的Markdown链接中的图片网址，并修改ReplyType为IMAGE_URL，以便CoW自动下载Markdown链接中的图片；
+ 去掉每行结尾的Markdown链接中网址部分的小括号，避免微信误以为“)”是网址的一部分导致微信中无法打开该页面。


**安装方法：**

```sh
#installp https://github.com/wangxyd/nicecoze.git
#scanp
```

**配置方法：**

无需任何配置！

**更新方法：**
```sh
#updatep nicecoze
```