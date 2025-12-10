
CaptchaVision 是一个基于 LLM 的验证码识别服务。提供图像预处理（二值化、去网格线）和 RESTful API，用于自动化验证码识别。

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






