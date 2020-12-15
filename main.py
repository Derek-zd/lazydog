# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import _thread
import json
import os
import sys
import time
import urllib.request

import configparser
import logging
import pymysql

# 初始化日志
logging.basicConfig(level=logging.INFO, format='%(asctime)-10s    %(levelname)-10s    %(name)-20s        %(message)-s')

DAEMON_URL = ""
MINER_URL = ""
MINER_TOKEN = ""
DAEMON_TOKEN = ""


def daemon_get_json(method, params):
    """Request daemon api"""
    return get_json(DAEMON_URL, DAEMON_TOKEN, method, params)


def miner_get_json(method, params):
    """ Request miner api"""
    return get_json(MINER_URL, MINER_TOKEN, method, params)


def get_json(url, token, method, params):
    """standard request api function"""
    jsondata = json.dumps({"jsonrpc": "2.0", "method": "Filecoin." + method, "params": params, "id": 3}).encode("utf8")
    req = urllib.request.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(req, jsondata)
    except urllib.error.URLError as e_url:
        print(f'ERROR accessing {url} : {e_url.reason}', file=sys.stderr)
        print(f'DEBUG: method {method} / params {params} ', file=sys.stderr)
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    try:
        res = response.read()
        page = res.decode("utf8")

        # parse json object
        obj = json.loads(page)
    except Exception as e_generic:
        print(f'ERROR parsing URL response : {e_generic}', file=sys.stderr)
        print(f'DEBUG: method {method} / params {params} ', file=sys.stderr)
        print(f'DEBUG: {page} ', file=sys.stderr)
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    # Check if the answer contain results / otherwize quit
    if "result" not in obj.keys():
        print(f'ERROR {url} returned no result', file=sys.stderr)
        print(f'DEBUG: method {method} / params {params} ', file=sys.stderr)
        print(f'DEBUG: {obj} ', file=sys.stderr)

        # inform the dashboard execution failed
        print('lotus_scrape_execution_succeed { } 0')
        sys.exit(0)

    # output some object attributes
    return obj


def readConf_db():
    _logger = logging.getLogger("readConf_db")
    # 获取当前文件的路径
    root_path = os.path.dirname(os.path.abspath(__file__))
    conf = configparser.ConfigParser()
    if root_path.find('\\') != -1:
        path = root_path + '\config\config.conf'

    else:
        path = root_path + '/config/config.conf'
    _logger.info(path)
    conf.read(path, encoding='utf-8')
    db_host = conf.get("DATABASE", "DB_HOST")
    db_name = conf.get("DATABASE", "DB_NAME")
    db_port = int(conf.get("DATABASE", "DB_PORT"))
    db_user = conf.get("DATABASE", "DB_USER")
    db_password = conf.get("DATABASE", "DB_PASS")
    db = {'db_host': db_host, 'db_name': db_name, 'db_port': db_port, 'db_user': db_user, 'db_password': db_password}
    return db


def height(threadName, delay):
    logger = logging.getLogger("height")
    logger.info("start get chain height")
    db_info = readConf_db()
    # 打开数据库连接
    conn = pymysql.connect(db_info['db_host'], db_info['db_user'], db_info['db_password'], db=db_info['db_name'],
                           port=db_info['db_port'])
    cursor = conn.cursor()
    logger.info(cursor)
    # 获取minerID
    while 1:
        # 获取tipset和chainhead
        chainhead = daemon_get_json("ChainHead", [])
        height = chainhead["result"]["Height"]
        logger.info("当前高度:{}".format(height))
        sql = "update chain_height set  height = {} ;".format(height)
        cursor.execute(sql)
        logger.info("高度插入成功")
        conn.commit()
        time.sleep(30)


def miner(cursor_miner):

    # 获取 miner 信息
    # 获取 miner id
    actoraddress = miner_get_json("ActorAddress", [])
    miner_id = actoraddress['result']

    miner_version = miner_get_json("Version", [])["result"]["Version"]

    # RETRIEVE MAIN ADDRESSES
    daemon_stats = daemon_get_json("StateMinerInfo", [miner_id, empty_tipsetkey])
    miner_owner = daemon_stats["result"]["Owner"]
    miner_owner_addr = daemon_get_json("StateAccountKey", [miner_owner, empty_tipsetkey])["result"]
    miner_worker = daemon_stats["result"]["Worker"]
    miner_worker_addr = daemon_get_json("StateAccountKey", [miner_worker, empty_tipsetkey])["result"]
    miner_sector_size = daemon_stats["result"]["SectorSize"]
    try:
        miner_control0 = daemon_stats["result"]["ControlAddresses"][0]
    except:
        miner_control0 = miner_worker
    miner_control0_addr = daemon_get_json("StateAccountKey", [miner_control0, empty_tipsetkey])["result"]
    sql = "insert into miner_info(miner_id, miner_version, miner_owner, miner_owner_addr, miner_worker,miner_worker_addr, miner_control0, miner_control0_addr,miner_sector_size) values('{}','{}','{}','{}','{}','{}','{}','{}','{}') on duplicate key update miner_version='{}', miner_owner='{}', miner_owner_addr='{}', miner_worker='{}',miner_worker_addr='{}', miner_control0='{}', miner_control0_addr='{}';".format(
        miner_id, miner_version, miner_owner, miner_owner_addr, miner_worker, miner_worker_addr, miner_control0,
        miner_control0_addr, miner_sector_size, miner_version, miner_owner, miner_owner_addr, miner_worker,
        miner_worker_addr, miner_control0, miner_control0_addr)
    cursor_miner.execute(sql)
    conn_miner.commit()
    logger.info("更新miner info 成功")

    # 获取钱包信息，导入数据库
    walletlist = daemon_get_json("WalletList", [])
    for addr in walletlist["result"]:
        balance = float(daemon_get_json("WalletBalance", [addr])["result"]) / 1000000000000000000
        short = str(addr[0:5] + "..." + addr[-5:])
        # 插入钱包余额，如果已存在钱包记录，只更新余额
        sql = "insert ignore into lotus_wallet_balance(wallet_addr, wallet_addr_short, balance) values('{}','{}','{}') on duplicate key update balance = '{}';".format(
            addr, short, balance, balance)
        cursor_miner.execute(sql)
        conn_miner.commit()
        logger.info("更新钱包余额成功")

    # 获取存力信息
    powerlist = daemon_get_json("StateMinerPower", [miner_id, empty_tipsetkey])
    minerpower = powerlist["result"]["MinerPower"]
    totalpower = powerlist["result"]["TotalPower"]

    sql = "insert ignore  into miner_power(miner_id,miner_RawBytePower,miner_QualityAdjPower,networker_RawBytePower,networker_QualityAdjPower) values('{}','{}','{}','{}','{}') on duplicate key update miner_RawBytePower= '{}' ,miner_QualityAdjPower = '{}' , networker_RawBytePower ='{}',  networker_QualityAdjPower = '{}';".format(
        miner_id, minerpower["RawBytePower"], minerpower["QualityAdjPower"], totalpower["RawBytePower"],
        totalpower["QualityAdjPower"], minerpower["RawBytePower"], minerpower["QualityAdjPower"],
        totalpower["RawBytePower"], totalpower["QualityAdjPower"])
    cursor_miner.execute(sql)
    conn_miner.commit()
    logger.info("更新存力成功")

    # 获取sector信息
    sector_list = miner_get_json("SectorsList", [])
    # sectors_counters = {}
    # remove duplicate (bug)
    unique_sector_list = set(sector_list["result"])

    for sector in unique_sector_list:
        detail = miner_get_json("SectorsStatus", [sector, False])
        state = detail["result"]["State"]
        deals = len(detail["result"]["Deals"]) - detail["result"]["Deals"].count(0)
        verified_weight = detail["result"]["VerifiedDealWeight"]
        if detail["result"]["Log"][0]["Kind"] == "event;sealing.SectorStartCC":
            pledged = 1
        else:
            pledged = 0
        sql = "insert ignore into sector_state(miner_id,sector_id,state,pledge,deals,verified_weight) values('{}',{},'{}',{},{},{}) on duplicate key update state='{}', pledge={},deals={},verified_weight={};".format(
            miner_id, sector, state, pledged, deals, verified_weight, state, pledged, deals, verified_weight)
        cursor_miner.execute(sql)
        conn_miner.commit()
    logger.info("更新sector状态成功")


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    logger = logging.getLogger('main')
    # global DAEMON_URL, MINER_URL, MINER_TOKEN, DAEMON_TOKEN
    empty_tipsetkey = []
    config = configparser.ConfigParser()
    config.read("./config/config.conf", encoding="utf-8")
    miner_api_ip = config.get("MINER_API", "MINER_API_IP")
    miner_api_port = config.get("MINER_API", "MINER_API_PORT")
    MINER_TOKEN = config.get("MINER_API", "MINER_API_TOKEN")
    MINER_URL = "http://" + miner_api_ip + ":" + miner_api_port + "/rpc/v0"
    logger.info("miner-api:{}".format(MINER_URL))

    daemon_api_ip = config.get("DAEMON_API", "DAEMON_API_IP")
    daemon_api_port = config.get("DAEMON_API", "DAEMON_API_PORT")
    DAEMON_TOKEN = config.get("DAEMON_API", "DAEMON_API_TOKEN")
    DAEMON_URL = "http://" + daemon_api_ip + ":" + daemon_api_port + "/rpc/v0"
    logger.info("daemon-api:{}".format(DAEMON_URL))

    _thread.start_new_thread(height, ("height", 2))

    db_info = readConf_db()
    conn_miner = pymysql.connect(db_info['db_host'], db_info['db_user'], db_info['db_password'], db=db_info['db_name'],
                                 port=db_info['db_port'])
    cursor_miner = conn_miner.cursor()

    while 1:
       miner(cursor_miner)

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
