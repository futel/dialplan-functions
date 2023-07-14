# SSL certificate

This is needed to publish dialplan documents with a custom domain name.

# Requirements

ubuntu 22
certbot
openssl

# Create or renew certificate

Create or renew a certificate for each of dev.dialplans.phu73l.net, stage.dialplans.phu73l.net, prod.dialplans.phu73l.net.

- sudo certbot certonly --manual --preferred-challenges dns
 - enter email for reminder
 - add txt record for dialplans.phu73l.net using digitalocean web console
 - complete certbot
 - remove txt record for dialplans.phu73l.net using digitalocean web console
- add expiration to calendar
- copy /etc/letsencrypt/archive/dev.dialplans.phu73l.net etc to conf
- in dev.dialplans.phu73l.net, cat cert1.pem chain1.pem fullchain1.pem > all.pem

# Import certificate to ACM

- visit ACM web console
- change region to us-east-1
- import a certificate
 - certificate body cert1.pem
 - certificate private key privkey1.pem
 - certificate chain all.pem
 
Note ARN. This is needed to deploy the AWS API Gateway.

# Delete certificates

- certbot certificates
- certbot delete --cert-name dev.dialplans.phu73l.net
- visit ACM web console

# Notes

The box that certbot is run on becomes a local registry for the certs, not sure what does the reminder email. Do we need the local certs when we renew or can they be thrown away after they're in ACM?

The cert expiry is short, this process must be repeated each time. I think the usual process is to have the infrastructure and staff, a networked box running certbot and a human to keep it running. Might be worth it to just buy 4 certs a year?

We can't deploy the AWS API Gateway if ACM has more than one cert for the domain name we are deploying to, e.g. if *.example com exists, we can't deploy dev.example.com. To replace an existing cert for an existing deployment, we must delete the existing deployment, then the existing cert, then re-create the cert and deployment. This is a problem with prod, we probably need to be able to create a second prod? prod should be prod-foo, prod-bar, etc?

https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains-prerequisites.html
https://eff-certbot.readthedocs.io/en/stable/using.html#manual
https://aws.github.io/chalice/topics/domainname.html
