# Draft preview container only. Pin the base image by digest and scan it before production.
FROM nginxinc/nginx-unprivileged:stable-alpine
COPY site/ /usr/share/nginx/html/
EXPOSE 8080
