# 毕设项目
    **旅行路线推荐**

#

### `crawler` 是爬虫目录
`travel_crawler.py` 是景点信息爬虫代码

`poi_score_crawler.py` 是景点评分爬虫代码

`poi_info.csv` 是从数据库导出的景点信息

`poi_scores.json` 和`poi_scores.py` 是景点评分的详细记录

#

### `txt_handler` 是文本处理目录
`poi_to_txt.py` 用来把景点信息导出为文本

`cut_words.py` 是将导出的信息文本进行分词的代码

`TF-IDF1.py` 包括提取景点文本关键词和关键词向量聚类

`add_cut_type.py` 是将信息文本聚类结果会写的代码

`small_dict.py` 是用于分词的小型自定义词典

`stop_words.txt` 是用于分词的小型停用词库

#

### `poi_files` 是景点信息文本

### `cut_results` 是景点信息文本分词的结果

#

### `db.py` 是Python ORM框架SQLAlchemy的Model

#

### `server` 是搭建于Flask的Web APP

`static` 目录是用于网页的静态文件(CSS和图片等)

`templates` 目录是Flask框架需要返回和渲染的HTML Jinja2模板，包括所有页面

`server.py` 是包括计算景点得分和路线以及启动Flask Web服务的代码

#

### 启动方法

在当前项目的`server`目录下，运行`python server.py`命令启动服务器
