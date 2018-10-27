import threading
import time
from datetime import datetime as dt
import logging
from cpchain.account import scan_transaction, web3
from django.db import transaction
import sys
import pytz
sys.path.append('.')

from .models import Record, Config
from .serializers import RecordSerializer


logger = logging.getLogger(__name__)


def scan():
    while True:
        tz = pytz.timezone('Asia/Shanghai')
        start = time.time()
        block_num = web3.eth.blockNumber
        try:
            qs = Config.objects.filter()
            if qs.count() == 0:
                config = Config(block_at=0, trans_cnt=0, start=dt.now(tz), end=dt.now(tz))
                config.save()
            else:
                config = qs[0]
                config.start = dt.now(tz)
                config.save()
            frm = config.block_at
        except Exception as e:
            logger.error(e)
            frm = 0

        logger.info('Scan Transactions at {}, from block {} to {}'.format(dt.now(tz), frm, block_num))
        try:
            records = scan_transaction(frm, block_num)
            for record in records:
                # with transaction.atomic():
                    block_id = record
                    if not isinstance(record, int):
                        block_id = record['block']
                    config = Config.objects.filter()[0]
                    config.block_at = block_id
                    config.end = dt.now(tz)
                    config.save()
                    if isinstance(record, int) or Record.objects.filter(txhash=record['txhash']).count() > 0:
                        continue
                    logger.debug('Save Record {}'.format(record['txhash']))
                    record['frm'] = record['from']
                    del record['from']
                    serializer = Record(**record)
                    serializer.save()
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(e)
        end = time.time()
        logger.info('Scan Transactions finished, {}'.format(end - start))
        time.sleep(5)

def run_monitor():
    logger.info('Run Monitor')
    monitor = threading.Thread(target=scan)
    monitor.start()
