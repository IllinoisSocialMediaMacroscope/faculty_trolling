nohup uwsgi --socket :8000 \
--chdir /home/ubuntu/faculty_trolling \
--module faculty_trolling.wsgi \
> uwsgi.out &
