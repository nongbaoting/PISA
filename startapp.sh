redis-server /etc/redis/redis.conf 
cd /apps/django_prot/
source /root/miniconda3/etc/profile.d/conda.sh
conda activate webProt
celery -A django_prot worker -l info  -c 2 -E > /apps/resultData/logs/celery.log 2>&1 &
python manage.py runserver 0:9006 >/apps/resultData/logs/django.log 2>&1 &


cd /apps/fontEnd 
npm run serve >/apps/resultData/logs/fontEnd.log 2>&1