### 监控系统资源

docker build -t monitor .

docker run -d -p 80:5000 --name monitor --restart unless-stopped monitor
