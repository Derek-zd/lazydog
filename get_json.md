# daemon
daemon_stats = daemon_get_json("StateMinerInfo", [miner_id, empty_tipsetkey])

chainhead = daemon_get_json("ChainHead", [])

sync_status = daemon_get_json("SyncState", [])

daemon_stats = daemon_get_json("StateMinerInfo", [miner_id, empty_tipsetkey])
miner_owner = daemon_stats["result"]["Owner"]
miner_owner_addr = daemon_get_json("StateAccountKey", [miner_owner, empty_tipsetkey])["result"]
miner_worker = daemon_stats["result"]["Worker"]
miner_worker_addr = daemon_get_json("StateAccountKey", [miner_worker, empty_tipsetkey])["result"]
miner_balance_available = daemon_get_json("StateMinerAvailableBalance", [miner_id, empty_tipsetkey])

locked_funds = daemon_get_json("StateReadState", [miner_id, empty_tipsetkey])

miner_balance_available = daemon_get_json("StateMinerAvailableBalance", [miner_id, empty_tipsetkey])

walletlist = daemon_get_json("WalletList", [])
balance = daemon_get_json("WalletBalance",[addr])

locked_funds = daemon_get_json("StateReadState", [miner_id, empty_tipsetkey])

base_info = daemon_get_json("MinerGetBaseInfo", [miner_id, chainhead["result"]["Height"], tipsetkey])
mpoolpending = daemon_get_json("MpoolPending", [empty_tipsetkey])
daemon_netpeers = daemon_get_json("NetPeers", [])
net_list = daemon_get_json("NetBandwidthStats", [])
protocols_list = daemon_get_json("NetBandwidthStatsByProtocol", [])
protocols_list = miner_get_json("NetBandwidthStatsByProtocol", [])


deal_info = daemon_get_json("StateMarketStorageDeal", [deal, empty_tipsetkey])

deadlines = daemon_get_json("StateMinerProvingDeadline", [miner_id, empty_tipsetkey])
proven_partitions = daemon_get_json("StateMinerDeadlines", [miner_id, empty_tipsetkey])
partitions = daemon_get_json("StateMinerPartitions", [miner_id, idx, empty_tipsetkey])

powerlist = daemon_get_json("StateMinerPower", [miner_id, empty_tipsetkey])

# miner
miner_netpeers = miner_get_json("NetPeers", [])
net_list = miner_get_json("NetBandwidthStats", [])

actoraddress = miner_get_json("ActorAddress", [])

miner_version = miner_get_json("Version", [])

workerstats = miner_get_json("WorkerStats", [])
workerjobs = miner_get_json("WorkerJobs", [])
scheddiag = miner_get_json("SealingSchedDiag", [True])
sector_list = miner_get_json("SectorsList", [])
storage_list = miner_get_json("StorageList", [])
storage_local_list = miner_get_json("StorageLocal", [])
storage_info = miner_get_json("StorageInfo", [storage])
storage_path = storage_local_list["result"][storage]

