#启动nginx
sudo nginx
# 先关闭uwsgi
# 如果压根就没有uwsgi.pid这个文件
# 说明项目还没启动 这一句会报错  直接忽略即可
uwsgi --stop uwsgi.pid
# 再启动项目
uwsgi --ini uwsgi.ini