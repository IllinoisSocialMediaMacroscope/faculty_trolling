nohup uwsgi --socket :8000 \
--chdir /home/ubuntu/faculty_trolling \
--module faculty_trolling.wsgi \
--check-static /home/ubuntu/faculty_trolling/faculty_trolling/static/ \
--static-map /static=/home/ubuntu/faculty_trolling/faculty_trolling/static/ \
> uwsgi.out &
