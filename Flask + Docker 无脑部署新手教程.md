（收藏数远远大于点赞数，嘤嘤嘤）
----------------

最近一个朋友在一直微信问我怎么部署flask。
-----------------------

这种情况我有经验：“google 啥都有，搜 flask 部署去”

朋友：“完全看不懂”

  

![](https://pic3.zhimg.com/v2-4f0c82ba86b07b9c24177d79c8cdebf0_1440w.jpg)

  

我直觉想反驳，可是想到当初我学部署的时候也一头雾水肝几天也没搞明白（当时是计算机网络、linux、python一窍不通），就理解了。其实在docker流行的今天，部署已经要比当初我学的时候要方便得多，但是前段时间我google搜了一圈的确没看到几篇比较好的 [Docker](https://zhida.zhihu.com/search?content_id=105558942&content_type=Article&match_order=1&q=Docker&zhida_source=entity) + Flask 的指导，于是写一篇菜鸟也能看懂的新手教程。

本教程的特点就是比较无脑，照着做就能部署成功。与其部署之前学一堆看不懂的，不如直接部署了找感觉。同时给出一些链接，想深入一点了解的可以自行深入学习。

基础介绍
----

*   Flask ：python最流行的两个框架之一（django、flask），**轻量级**是最大的特点
*   [Gunicorn](https://zhida.zhihu.com/search?content_id=105558942&content_type=Article&match_order=1&q=Gunicorn&zhida_source=entity)：只熟悉熟悉用 java 或者 PHP 做开发的可能对 python 的部署一开始不太理解，Flask应用是一个符合[WSGI](https://zhida.zhihu.com/search?content_id=105558942&content_type=Article&match_order=1&q=WSGI&zhida_source=entity)规范的Python应用，不能独立运行（类似app.run的方式仅适合开发模式），需要依赖其他的组件提供服务器功能。
*   gevent：gunicorn 默认使用同步阻塞的网络模型(-k sync)，对于大并发的访问可能表现不够好，我们很方便地顺手套一个gevent来增加并发量
*   Docker：容器，可以理解成一个“黑盒”。在项目变得庞大以后，往往我们会疲于管理整个项目的部署和维护。如果我们将整个项目用一个“容器”装起来，那么我们仅仅只用维护一个配置文件告诉计算机每次部署要把什么东西装进“容器”，甚至借用一些工具把这个过程自动化，部署就会变得很方便。这也是为什么我写这篇文章的原因

整个架构如图所示：

  

![](https://pic2.zhimg.com/v2-cfe2a118ec820eeb9567bd466399b779_1440w.jpg)

  

具体操作
----

下面我们首先在自己电脑就可以运行，不用登陆服务器终端

以小学期的一个 web 项目为例，我们的项目架构是这样的：

  

![](https://pic1.zhimg.com/v2-e39a332b3ce3b96f9207e57daf6fca08_1440w.jpg)

  

我们先看根目录下的 [start.py](http://start.py/)，这是项目的启动文件：

```python
#start.py
from project import create_app #从project文件夹中的__init__.py中导入create_app函数

app = create_app() #记住这里的变量名app

if __name__ == '__main__':
    app.run(debug=True)
```

其中，我们 project 里面的 flask 项目用了 [blueprint](https://zhida.zhihu.com/search?content_id=105558942&content_type=Article&match_order=1&q=blueprint&zhida_source=entity) 的方式去构建，所以我们用了**init**.py 来定义这个flask项目，这里相当于将 web 项目用文件夹“封装”了起来，部署的内容只和文件夹里面有关。

不过可能更常见的新手教程里面的是这个样式：

```python
#start.py
from flask import Flask

app = Flask(__name__) #记住这里的变量名app

@app.route('/')
def hello():
    return 'hello docker&flask'

if __name__ == '__main__':
    app.run(debug=True)
```

用哪种都无所谓，如果没接触过蓝图直接用第二种常规的方式即可（注意如果用第二种方式，几个用来部署的文件和 Flask 项目应是同级文件夹的。

一旦使用命令`python start.py`运行这个应用，打开浏览器，输入网址`127.0.0.1:5000`并回车，将会打开我们的网站。

但是这样简单运行的话，只要按一下 ctrl + c 终止运行，或者关掉终端，网站就连接不了了，我们要寻求更长久的真正的部署。

Gunicorn + Gevent
-----------------

运行以下命令即可安装这两个利器

```bash
pip install gunicorn gevent
```

在根目录下新建文件 `/gunicorn.conf.py`

```bash
workers = 5    # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
worker_class = "gevent"   # 采用gevent库，支持异步处理请求，提高吞吐量
bind = "0.0.0.0:80"
```

可以使用gunicorn命令来测试是否可以正确运行，命令如下，打开网址`127.0.0.1:80`，将会打开我们的网站。

```bash
gunicorn start:app -c gunicorn.conf.py
```

_一旦报错，则根据错误提示修复即可。_

使用 Docker 封装 Flask 应用
---------------------

当然第一步先安装 docker。

下面我们将项目用 docker 包装好，以便扔到服务器上直接跑（学生党可以买阿里云或者腾讯云，均有学生优惠）。

首先我们需要为该应用创建一个 requirements.txt 文件，以便容器里面 python 环境的安装：`/requirements.txt`

```bash
gunicorn
gevent
flask
# ...以下替换成项目需要安装的所有 python 库，如 flask-wtf，flask-login...whatever
```

requirements.txt 是做 python 项目常写的一个文件，有了这个文件，在安装 python 应用依赖的三方包时，可以直接用如下命令执行：

```bash
pip install -r requirements.txt
```

当然我们这里先不用执行。

然后我们还要创建一个 [Dockerfile](https://zhida.zhihu.com/search?content_id=105558942&content_type=Article&match_order=1&q=Dockerfile&zhida_source=entity) 文件，以便 Docker 镜像的构建：`/Dockerfile`

```bash
FROM python:3.6
WORKDIR /Project/demo

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "start:app", "-c", "./gunicorn.conf.py"]
```

其中，第二行 WORKDIR 后面写的是要部署到服务器上的路径，最后一行里面的 start 是我们上面写的 python 启动文件名，app 是启动文件里面要启动的应用名（变量名）

完成这两个文件的创建之后，执行如下命令，就可以开始构建Docker镜像：

```bash
sudo docker build -t 'testflask' .
```

需要注意的是这个过程需要一点时间，因_为它有几百兆。_ 构建完成之后，通过如下命令查看镜像列表，可以发现 testflask 显示在其中：

```bash
sudo docker images
```

将镜像 push 到 docker cloud 上（没有账号的要先注册），这个过程由于官方文档很齐备了，我就直接放链接了，几步就可。（操作和 git 非常类似）

[https://docs.docker.com/v17.12/docker-cloud/builds/push-images/](https://docs.docker.com/v17.12/docker-cloud/builds/push-images/)

部署到服务器上
-------

最后一步了，这里假设服务器是 ubuntu 系统，首先安装 docker

```bash
sudo apt-get install docker.io
```

然后登陆我们准备好的远程服务器终端，把镜像 pull 下来，两三个命令就可，这里还是直接放个简易教程

[https://www.shellhacks.com/docker-pull-command-examples/](https://www.shellhacks.com/docker-pull-command-examples/)

接下来我们可以直接运行了：

*   临时运行docker镜像：

sudo docker run -it --rm -p 80:80 testflask

可以看到Docker镜像成功地运行起来了，并处于阻塞状态。这时，我们打开浏览器，输入服务器外网 ip，可以我们的网站已经部署上去。

*   生产环境运行(以daemon方式运行)

sudo docker run -d -p 80:80 --name test-flask-1 testflask

最后提一点，新手在这里有个坑，记得在服务器的仪表盘（dashboard）的设置里面开启相应的外网端口（这里是 80）

那么到这里 Flask 项目已经成功部署。更新项目的时候，维护好配置文件，build一下，push 上去，在服务器 pull 下来，重新运行即可。

  

**如果觉得有帮助，关注公众号就是最大的支持。**

![](https://picx.zhimg.com/v2-90469572d267c1df8711a9f6dc713b71_1440w.jpg)

![](https://pic3.zhimg.com/v2-73ab07a815941a50750cadbe0729a388_1440w.jpg)

本文转自 <https://zhuanlan.zhihu.com/p/78432719>，如有侵权，请联系删除。