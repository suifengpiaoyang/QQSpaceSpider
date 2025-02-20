# QQ 空间图片爬虫
## 功能：
下载 QQ 空间里面的照片。  
* 支持更新，更新不会覆盖原来已下载的图片。
* 支持断点下载，可以随意运行或停止脚本，脚本将会自动检测需要下载的图片。
## 使用方式：
1. 设置好 SAVE_PATH ，如果放空，则保存在当前路径下。 
2. 在浏览器上登录 QQ 空间，将已经成功登录的 cookie 复制进 cookies.txt 里面。  
至于如何从浏览器获得 cookie ，请自行搜索。
3. 填写好 spider.download_picture ，可以顺序填写多个。
4. 运行脚本

## spider.download_picture 填写方式及示例：
```python
spider.download_picture(target_qq, include_list=None, exclude_list=None, exclude_key=None, name_mode=1)
```
填写好 target_qq 就可以直接运行了，默认爬取所有的图片。暂时对于需要输入密码的相册支持不理想。  
里面几个可选参数的含义：  
* include_list：包含列表。只下载列表里相册名的图片，相册名需与 QQ 空间的相同。  
* exclude_list：排除列表。不下载列表里相册明的图片，相册名需与 QQ 空间的相同。  
* exclude_key：排除关键词。不下载含有该关键词的相册名的图片。  
* name_mode：图片的命名方式，目前暂只有一个模式。 
#### Example:
下载所有图片
```python
spider.download_picture('XXXXXXXX')
```
下载相册名称为 test1 和 test2 的图片
```python
spider.download_picture('XXXXXXXX', include_list=['test1', 'test2'])
```
下载相册名不含有 test 的图片
```python
spider.download_picture('XXXXXXXX', exclude_key='test')
```

## 未完善之处：
* 对有密码验证的相册支持不好，可能会报错。目前没有多加测试。
* 如果 QQ 相册中有视频，这部分还没完善。暂时没需求，故没有去上传测试。

## 总论：

在下面的爬虫里，有几点为了方便做得不像浏览器访问：
* 在一个 get 的参数中，我将 pageStart 的值设置为 0，以获得所有的元素，不然按照原来的数值，得到的结果是被分成多段的。
* 同样，我又将 pageNum 值设置为一个比较大的数，目的也是和上面一样。将 format 从 jsoup 改为 json ，方便我读取数据。
这些改变虽然 api 都可以认，并且也都达到预定的目的。但这些数值的改变不是正常浏览器产生的结果。这个是要知道的。
 
总之，我已努力将爬虫拟人化了。对于运行结果，暂时满意。仍许多需要改进的地方。

对于这些需要不时更新的图片爬虫，为图片命名是一个让我头疼的问题。
既要顾及到图片排序要和页面初始排序相同，该命名又能做检查之用，如果已经下载过下次访问就不再下载。
考虑了许多，我将图片的上传时间稍作修改作为图片名，这个时间是系统反馈的数据中就有的。

**后来我发现相册的排序是有另外的 js 代码所控制，这部分目前没有完成。**
