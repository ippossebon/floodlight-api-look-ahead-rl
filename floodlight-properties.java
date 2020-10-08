floodlight.modules=\
net.floodlightcontroller.jython.JythonDebugInterface,\
net.floodlightcontroller.storage.memory.MemoryStorageSource,\
net.floodlightcontroller.core.internal.FloodlightProvider,\
net.floodlightcontroller.threadpool.ThreadPool,\
net.floodlightcontroller.debugcounter.DebugCounterServiceImpl,\
net.floodlightcontroller.perfmon.PktInProcessingTime,\
net.floodlightcontroller.debugevent.DebugEventService,\
net.floodlightcontroller.staticflowentry.StaticFlowEntryPusher,\
net.floodlightcontroller.restserver.RestApiServer,\
net.floodlightcontroller.topology.TopologyManager,\
net.floodlightcontroller.forwarding.Forwarding,\
net.floodlightcontroller.linkdiscovery.internal.LinkDiscoveryManager,\
net.floodlightcontroller.ui.web.StaticWebRoutable,\
net.floodlightcontroller.loadbalancer.LoadBalancer,\
net.floodlightcontroller.firewall.Firewall,\
net.floodlightcontroller.devicemanager.internal.DeviceManagerImpl,\
net.floodlightcontroller.accesscontrollist.ACL,\
net.floodlightcontroller.statistics.StatisticsCollector
org.sdnplatform.sync.internal.SyncManager.authScheme=CHALLENGE_RESPONSE
org.sdnplatform.sync.internal.SyncManager.keyStorePath=/etc/floodlight/auth_credentials.jceks
org.sdnplatform.sync.internal.SyncManager.dbPath=/var/lib/floodlight/
org.sdnplatform.sync.internal.SyncManager.port=6642
net.floodlightcontroller.forwarding.Forwarding.match=vlan, mac, ip, transport
net.floodlightcontroller.forwarding.Forwarding.flood-arp=NO
net.floodlightcontroller.core.internal.FloodlightProvider.openFlowPort=6653
net.floodlightcontroller.core.internal.FloodlightProvider.role=ACTIVE
net.floodlightcontroller.linkdiscovery.internal.LinkDiscoveryManager.latency-history-size=10
net.floodlightcontroller.linkdiscovery.internal.LinkDiscoveryManager.latency-update-threshold=0.5
net.floodlightcontroller.core.internal.OFSwitchManager.defaultMaxTablesToReceiveTableMissFlow=1
net.floodlightcontroller.core.internal.OFSwitchManager.maxTablesToReceiveTableMissFlowPerDpid={"00:00:00:00:00:00:00:01":"1","2":"1"}
net.floodlightcontroller.core.internal.OFSwitchManager.clearTablesOnInitialHandshakeAsMaster=YES
net.floodlightcontroller.core.internal.OFSwitchManager.clearTablesOnEachTransitionToMaster=YES
net.floodlightcontroller.core.internal.OFSwitchManager.keyStorePath=/path/to/your/keystore-file.jks
net.floodlightcontroller.core.internal.OFSwitchManager.keyStorePassword=your-keystore-password
net.floodlightcontroller.core.internal.OFSwitchManager.useSsl=NO
net.floodlightcontroller.core.internal.OFSwitchManager.supportedOpenFlowVersions=1.0, 1.1, 1.2, 1.3, 1.4
net.floodlightcontroller.restserver.RestApiServer.keyStorePath=/path/to/your/keystore-file.jks
net.floodlightcontroller.restserver.RestApiServer.keyStorePassword=your-keystore-password
net.floodlightcontroller.restserver.RestApiServer.httpsNeedClientAuthentication=NO
net.floodlightcontroller.restserver.RestApiServer.useHttps=NO
net.floodlightcontroller.restserver.RestApiServer.useHttp=YES
net.floodlightcontroller.restserver.RestApiServer.httpsPort=8081
net.floodlightcontroller.restserver.RestApiServer.httpPort=8080
net.floodlightcontroller.statistics.StatisticsCollector.enable=TRUE
net.floodlightcontroller.statistics.StatisticsCollector.collectionIntervalPortStatsSeconds=5
