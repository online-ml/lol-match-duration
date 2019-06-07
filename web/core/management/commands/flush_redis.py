from django.conf import settings
from django.core.management import base
import redis


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Flushing redis')

        for conf in settings.RQ_QUEUES.values():
            redis.StrictRedis(
                host=conf['HOST'],
                port=conf['PORT'],
                db=conf['DB'],
                password=conf['PASSWORD']
            ).flushdb()
