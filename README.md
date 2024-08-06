一款用来适配Dify的chatbot的返回的markdown格式返回的消息处理

+ 提取Dify返回的Markdown图片链接中的网址，并修改ReplyType为IMAGE_URL，以便DoW自动下载Markdown链接中的图片；
+ 提取Dify返回的包含网址的Markdown链接中的图片网址，并修改ReplyType为IMAGE_URL，以便CoW自动下载Markdown链接中的图片；
+ 去掉每行结尾的Markdown链接中网址部分的小括号，避免微信误以为“)”是网址的一部分导致微信中无法打开该页面。
+ 增加分段发送消息,分割符为markdown语法中的换行标签`<br>`
+ 针对触发绘画的有loading消息触发
+ 支持图文消息拆分发送,Dify兼容性更好了
+ 增加对视频的支持
+ 兼容coze和更广泛的md格式

**安装方法：**

```sh
#installp https://github.com/AceyKubbo/dow-markdown.git
#scanp
```

**配置方法：**

无需任何配置！

**更新方法：**
```sh
#updatep dow_markdown
```
