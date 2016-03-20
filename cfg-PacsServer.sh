Settings on DCM4CHEE Server: 
Using JMX-Console:
1. Set following attributes in dcm4chee.archive:service=DcmServer:
SecurityProtocol = dicom-tls

2. Set following attributes in dcm4chee.archive:service=TLSConfig:
EnabledProtocols= SSLv2Hello,SSLv3,TLSv1
KeyStoreURL=resource:node1.jks
KeyStorePassword=your password
TrustStoreURL=resource:trust.jks
TrustStorePassword=your password

3. Generate a keystore and truststore file (use the password you specified in the TLSConfig service):
# keytool -genkey -keyalg RSA -dname "CN=imgstore00 OU=PACS O=Cancer Center of Hawaii L=honolulu C=US"--keystore node1.jks -alias node1




Enter keystore password: 
Re-enter new password:
Enter key password for <node1>
    (RETURN if same as keystore password): 

# keytool -export -file node1.cert -keystore node1.jks -alias node1
Enter keystore password: 
Certificate stored in file <node1.cert>

# keytool -import -file node1.cert -keystore trust.jks -alias node1
Enter keystore password: 
Re-enter new password:


Owner: CN="node1.dcm4che.org OU=development O=dcm4che L=Vienna C=AT"
Issuer: CN="node1.dcm4che.org OU=development O=dcm4che L=Vienna C=AT"
Serial number: 480c457d
Valid from: Mon Apr 21 09:42:53 CEST 2008 until: Sun Jul 20 09:42:53 CEST 2008
Certificate fingerprints:
     MD5:  79:8B:FC:11:65:51:1C:01:C5\:D1:FC:38:58:39:46:8E
     SHA1: E9:6E:54:BD:A7:35:BB:34:4E:4C:41:BD:0B:3A:2D:A3\:D4:1A:5F:8E
     Signature algorithm name: SHA1withRSA
     Version: 3
Trust this certificate? [no]:  yes
Certificate was added to keystore

4. Copy Key/Truststore files to dcm4chee installation directory:
cp node1.jks trust.jks DCM4CHEE_HOME/server/default/conf

5. Restart the dcm4chee server process

Testing with dcm4che 2 library software:
1. Copy Key/Truststore files to dcm4che 2 samples directory:
cp node1.jks trust.jks DCM4CHE_2/etc/tls

2. Execute dcmqr to do a DICOM Echo:
# DCM4CHE_2/bin/dcmqr DCM4CHEE@localhost:11112  -acceptTO 60000 -tls 3DES -truststore resource:tls/trust.jks -keystore resource:tls/node1.jks
