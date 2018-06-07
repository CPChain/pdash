import os
import re

def get_cpu_info():
    output = os.popen('cat /proc/cpuinfo')
    lines = output.readlines()
    output.close()

    cpu_num = 0
    for line in lines:
        try:
            key, value = line.split(':')
        except:
            # skip blank line
            pass
        else:
            if re.search('processor', key):
                cpu_num += 1
            elif re.match('cpu MHz', key):
                cpu_freq = float(value) / 1024

    return {'num': cpu_num, 'freq': cpu_freq}

def get_mem_info():
    output = os.popen('cat /proc/meminfo')
    lines = output.readlines()
    output.close()

    for line in lines:
        key, value = line.split(':')
        if re.search('MemTotal', key):
            mem_size = float(value.split()[0]) / 1024 / 1024

    return {'size': mem_size}

def get_nic_info(dst):
    output = os.popen("ip route get " + dst)
    lines = output.readlines()
    output.close()

    for line in lines:
        if re.search(dst, line):
            nic = line.split()[-3]

    try:
        output = os.popen('cat /sys/class/net/' + nic + '/speed')
        nic_speed = int(output.read())
        output.close()
    except:
        # for loopback interface
        nic_speed = 0

    return {'speed': nic_speed}

def search_peer(sysconf, peers_conf):

    pick_peer = None

    for peer_id in peers_conf: # pylint: disable=too-many-nested-blocks
        peer_conf = peers_conf[peer_id]
        match = True
        for hw in sysconf:
            if hw in peer_conf:
                try:
                    for key in sysconf[hw]:
                        if key in peer_conf[hw]:
                            if sysconf[hw][key] > peer_conf[hw][key]:
                                match = False
                                break
                        else:
                            match = False
                            break
                except:
                    match = False
                    break
            else:
                match = False
                break

        if match:
            # found the peer
            pick_peer = peer_id
            break

    return pick_peer
