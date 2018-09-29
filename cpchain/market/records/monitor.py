import threading
import time
from datetime import datetime as dt
import logging
from cpchain.account import scan_transaction
import sys
sys.path.append('.')

from .models import Record
from .serializers import RecordSerializer


logger = logging.getLogger(__name__)


def scan():
    while True:
        start = time.time()
        logger.info('Scan Transactions at {}'.format(dt.now()))
        try:
            records = scan_transaction()
            for record in records:
                if Record.objects.filter(txhash=record['txhash']).count() > 0:
                    continue
                logger.debug('Save Record {}'.format(record['txhash']))
                record['frm'] = record['from']
                del record['from']
                serializer = RecordSerializer(data=record)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
        except Exception as e:
            logger.error(e)
        end = time.time()
        logger.info('Scan Transactions finished, {}'.format(end - start))
        time.sleep(5)

def run_monitor():
    logger.info('Run Monitor')
    monitor = threading.Thread(target=scan)
    monitor.start()
