FROM nginx:1.11.3
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY sknightmare.conf /etc/nginx/conf.d

COPY ./kitchen_nightmare_gui /static/kitchen_nightmare_gui


