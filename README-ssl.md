# SSL certificate

This is needed to publish dialplan documents with a custom domain name.

# Meta-requirements

AWS ACM console access must have been set up.

DigitalOcean must have the dialplans.phu73l.net domain name set up.

This project must have been set up for all of dev, stage, prod deployments as described in README-deploy.

# Requirements

- ubuntu 22
- openssl
- certbot
- python3-certbot-dns-digitalocean
- DigitalOcean access token with all the domain scopes in conf/certbot-creds.ini

# Create certificate

- sudo certbot certonly --manual --preferred-challenges dns
 - domain names "*.dialplans.phu73l.net dialplans.phu73l.net phu73l.net"
 - enter email for reminder
 - add txt record for dialplans.phu73l.net using digitalocean web console
 - complete certbot
 - remove txt record for dialplans.phu73l.net using digitalocean web console
- add expiration to calendar
- in /etc/letsencrypt/live/dialplans.phu73l.net, cat cert.pem chain.pem fullchain.pem > all.pem

XXX manual is the hard way to do certbot
- sudo certbot certonly --dns-digitalocean --dns-digitalocean-credentials conf/certbot-creds.ini -d your_domain -d subdomain.your_domain -d '*.your_domain'
- XXX does that set up email remindering?

# Import a new or reimport an existing certificate to AWS

- visit AWS certificate manager (ACM) web console
- change region to us-east-1
- import a certificate, or list, visit, reimport certificate
 - certificate body cert.pem
 - certificate private key privkey.pem
 - certificate chain all.pem
 
If this is a new certificate, note the ARN. This is needed to deploy the AWS API Gateway.

# Update functions to use new certificate

If this is a new certificate, update app/.chalice/config.json to use the new certificate ARN for the deployment. Deploy affected stages as described in README-deploy.

# Renew certificate

Certificates must be renewed before they expire.

sudo certbot renew --cert-name dialplans.phu73l.net --dns-digitalocean --dns-digitalocean-credentials conf/certbot-creds.ini

- add expiration to calendar, "certbot certificates" to show the date
- in /etc/letsencrypt/live/dialplans.phu73l.net, cat cert.pem chain.pem fullchain.pem > all.pem
- Reimport the certificate as Import a new or reimport an existing certificate to ACM
- XXX did that set up email remindering?

# Delete certificates

- certbot certificates
- certbot delete --cert-name dev.dialplans.phu73l.net
- visit ACM web console

# List certificates

- certbot certificates
- visit AWS ACM web console
- change region to us-east-1

# Test

POST to a smoke test URL as described in README-test.

# Notes

The box that certbot is run on stores the creds and becomes a local registry for the certs, when we register on create/update, Let's Encrypt sends the reminder email. Do we need the local certs when we renew or can they be thrown away after they're in ACM? Files are stored in /etc/letsencrypt.

The cert expiry is short, this process must be repeated each time. I think the usual process is to have the infrastructure and staff, a networked box running certbot and a human to keep it running? It doesn't look hard if we aren't really concerned about security, need to run it with an auth hook periodically for autoewnewal. Might be worth it to just buy 4 certs a year?

https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains-prerequisites.html
https://eff-certbot.readthedocs.io/en/stable/using.html#manual
https://aws.github.io/chalice/topics/domainname.html
