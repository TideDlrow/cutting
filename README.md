用于切分视频或音频。

### 项目说明

config.py 文件配置了上传文件的保存路径，切分后的文件也会保存在这个目录中

页面主要的逻辑在views.py中

切分主要是通过ffmpeg完成的，所以确保机器安装了ffmpeg，和其有关的主要代码在utils.py中。

需要注意的是

文件上传的是直接以文件名存储在对应的保存路径下的，所以上传同名文件会覆盖原来存在的文件；

同时上传多个文件，只会以第一个为准，其它的都会忽略。

### 部署说明
####安装python及包管理
#### uwsgi
```shell
pip install uwsgi
uwsgi --version    # 查看 uwsgi 版本
```
#### 安装Django
```shell
pip install django
```
#### 安装Nginx
ubuntu下可以直接用命令
```shell
apt-get install nginx
```

#### 配置
自己新建一个uwsgi.ini，文件名和所在位置在哪都无所谓
```shell
[uwsgi]
# 对外提供的服务的端口，
socket = 127.0.0.1:8001
# 项目的路径，用绝对路径
chdir = ./

# Django s wsgi file
module = cutting.wsgi

# process-related settings
# master
master = true
# maximum number of worker processes
processes = 4
# ... with appropriate permissions - may be needed
# chmod-socket    = 664# clear environment on exit
vacuum = true
# 日志路径，最好也用绝对路径
daemonize = ./uwsgi.log
```

nginx配置nginx.conf（这个文件找不到用命令`sudo find / -name nginx.conf`搜一下）

关键是server的配置，其它的可以用默认的
```shell
http {

        ##
        # Basic Settings
        ##

        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 600; #这里默认是65秒，为了不会上传失败改成了600秒
        types_hash_max_size 2048;
        client_max_body_size 2048M;
        # server_tokens off;

        # server_names_hash_bucket_size 64;
        # server_name_in_redirect off;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ##
        # SSL Settings
        ##

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;

        ##
        # Logging Settings
        ##

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

        ##
        # Gzip Settings
        ##

        gzip on;

        # gzip_vary on;
        # gzip_proxied any;
        # gzip_comp_level 6;
        # gzip_buffers 16 8k;
        # gzip_http_version 1.1;
        # gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        ##
        # Virtual Host Configs
        ##

        # 关键的是下面这些配置        
        server{
                listen 80;#nginx监听的端口
                server_name cutting;
                charset utf-8;
                location / {
                        include uwsgi_params;
                        uwsgi_pass 127.0.0.1:8001;# 这里要和uwsgi.ini中socket的配置一样
                        uwsgi_param UWSGI_SCRIPT cutting.wsgi;
                        uwsgi_param UWSGI_CHDIR /home/xyong/data/wwwroot/cutting;#项目的路径
                }
        }
}
```

配置完成后先命令启动项目
```shell
uwsgi --ini uwsgi.ini
```
再启动nginx(如果已经启动，则用以下命令让其重新读取配置文件)
```shell
nginx -s reload
```
