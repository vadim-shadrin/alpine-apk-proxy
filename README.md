# alpine-apk-proxy
You can use this service as caching proxy for alpine linux artefacts

just change your /etc/apk/repositories

cat /etc/apk/repositories
```
http://alpine-apk-proxy.yourdmain:8080/v3.22/main
http://alpine-apk-proxy.yourdmain:8080/v3.22/community
```
