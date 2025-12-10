https://platform.openai.com/api-keys

这是openai的key。

火山的key管理：https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D


问题是镜像里缺少 libGL.so.1。已更新 Dockerfile，安装 libgl1（并保留原 opencv 依赖），重新构建即可：


```
# 第一步
cp .env.example .env
#第二步
docker build -t validata:latest .
# 第三部
docker run -d \
  --name validata_app \
  -p 8011:8011 \
  --env-file .env \
  validata:latest
```

若仍有缺依赖，可附加 libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 已包含，不需额外动作。



