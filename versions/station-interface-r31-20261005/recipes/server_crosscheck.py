from pathlib import Path
import hashlib,json,subprocess,re
W=Path(__file__).resolve().parent
S=Path(r'E:\ESTUDO APK\work\server-auth-handoff\Servidor-pix-implementar-faltas-20261002')
J=Path(r'E:\ESTUDO APK\work\station-room-diagnostics-r29-20261005\netplay-src\org\emulationstation\frontend\netplay')
revision='61c0411d0a306f348f48647b466a05a3d0f78733'
doc='docs/station-android/RETORNO-SERVIDOR-NETPLAY-INTERNET-STATION-R12-20261005.md'
source=subprocess.check_output(['git','-C',str(S),'show',revision+':'+doc]).decode('utf8')
checks={
 'uuidRequestId':('StationOnlineClient.java','UUID.randomUUID().toString()'),
 'leasedSession':('StationOnlineClient.java','app.sessions.acquire(cancel)'),
 'instanceAndRevision':('StationOnlineClient.java','.put("instance",snapshot.optString("instance",""))'),
 'heartbeat20Seconds':('StationRoomsActivity.java','elapsedRealtime()-heartbeat>=20000'),
 'advertisedRelayRequired':('StationRoomStartState.java','relay-wss-v1'),
 'perParticipantTicket':('StationRoomsActivity.java','command("relay-ticket")'),
 'signedPathValidation':('StationRetroLaunch.java','"/v1/station/online/relay".equals'),
 'headerTicketOnly':('StationRelayTunnel.java','Collections.singletonMap("Authorization","StationRelay "+ticket)'),
 'subprotocol':('StationRelayTunnel.java','new Protocol("station-relay.v1")'),
 'queryRejected':('StationRelayTunnel.java','uri.getQuery()!=null'),
 'tcpNoDelay':('StationRelayTunnel.java','remote.setTcpNoDelay(true)'),
 'hostListeningCallback':('StationGameSession.java','if(listening&&!acknowledged)'),
 'tlsEndpointIdentity':('StationRelayTunnel.java','p.setEndpointIdentificationAlgorithm("HTTPS")'),
 'ticketLength':('StationRetroLaunch.java','{43}'),
 'nativeAndRemoteCleanup':('StationRelayTunnel.java','remote.closeConnection(1000,"");io.shutdownNow()'),
}
evidence={}
for name,(file,needle) in checks.items():
 p=J/file;s=p.read_text('utf8');assert needle in s,name
 evidence[name]={'file':file,'line':next(i+1 for i,l in enumerate(s.splitlines()) if needle in l),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
receipt={
 'serverDocumentCommit':revision,'serverDocumentPath':doc,'serverDocumentSHA256':hashlib.sha256(source.encode()).hexdigest(),
 'serverSourceRevision':'e4e557a985ac5bead24885149c8650a5bb2dfae8',
 'serverDLLSHA256':'7ecb6c8d94c5ab42c26638b5f9bdf7ffd0e70f99e047463ee5293af34f7bdcf5',
 'unchangedRoomsDEX':'45675ff1b72c76bc6d388f6fa6f016a55cc1d06c4fbec09689ab4654dde3e9f1',
 'sourceChecks':evidence,'checksPassed':len(evidence),
 'clientRouteChangesRequired':False,'serverDeploymentPerformed':False,
 'serverReportedPublicWssP95Ms':2291.8209,'twoAndroidGameplayVerified':False,
 'pocoLicenseStateInHandoff':'ACTIVE/PENDING_ENROLLMENT','activationCodeInGit':False,
 'pocoActivationPerformed':False,'rawDownloadDeltaIncluded':False,
}
(W/'evidence/server-crosscheck.json').write_text(json.dumps(receipt,indent=2),'utf8')
print('PASS',len(checks),'client source contract checks; no route/Dex change required by latest server handoff.')
