FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY . .

EXPOSE 80

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app