# SSL certificate

Certificates are needed to for AWS Lambda to publish HTTPS with a custom domain name.

# Meta-requirements

AWS ACM console access must have been set up.

Domains should be created with DigitalOcean:
- dialplans.phu73l.net
- ops.phu73l.net

# Requirements


- debian box (trixie, ubuntu 23)
- openssl (3.2.2-1)
- snapd apt package
  - sudo apd install snapd
- snapd snap package
  - sudo snap install snapd
- certbot and plugin snap (2.11.0)
  - sudo snap install --classic certbot
  - sudo ln -s /snap/bin/certbot /usr/bin/certbot
  - sudo snap set certbot trust-plugin-with-root=ok
  - sudo snap install certbot-dns-digitalocean
- DigitalOcean access token with all the domain scopes in conf/certbot-creds.ini

---

# Create certificate

This needs to be done when the certificate doesn't exist yet or after attributes have changed. The certificate is registered with let's encrypt, but not yet used to publish HTTPS.

This is done on whatever box will handle renewals. This deployment process doesn't include requirements to make automatic renewal reliable, it is probably running on a laptop, so manual renewals or at least verification of automatic renewals are assumed.

- sudo certbot certonly --dns-digitalocean --dns-digitalocean-credentials conf/certbot-creds.ini -d phu73l.net -d dialplans.phu73l.net -d '*.dialplans.phu73l.net' -d ops.phu73l.net -d '*.ops.phu73l.net'
  - answer questions
- add expiration to a human's calendar
- sudo cat /etc/letsencrypt/live/phu73l.net/cert.pem /etc/letsencrypt/live/phu73l.net/chain.pem /etc/letsencrypt/live/phu73l.net/fullchain.pem >/tmp/all.pem

# Import or reimport and deploy certificate

This needs to be done after a certificate is created or renewed. The certificate is given to AWS, but not yet used to publish HTTPS.

- visit AWS certificate manager (ACM) web console
- change region to us-east-1
- import a certificate, or list, visit, reimport certificate with domain phu73l.net
 - certificate body /etc/letsencrypt/live/phu73l.net/cert.pem
 - certificate private key /etc/letsencrypt/live/phu73l.net/privkey.pem
 - certificate chain /tmp/all.pem
 
If this is a new certificate, note the ARN. This is needed to deploy the AWS API Gateway.

# Update Lambda functions to use new certificate

This needs to be done after a certificate is created or replaced, not after reimport. The certificate is used by AWS to publish HTTPS.

- update config files:
  - app-dialplan/.chalice/config.json
  - app-ops/.chalice/config.json  
  - Update every certificate_arn
- deploy affected stages as described in DEPLOY.md.

---

# Renew and deploy certificate

Certificates must be renewed before they expire.

This should have been set up by the certificate creation method using systemd, but hasn't been tested. Notice the renewal warning email, check, and be prepared to manually renew at the end of the certificate's life. This deployment process doesn't include requirements to make automatic renewal reliable, it is probably running on a laptop, and we need to reimport to aws after renewal?

sudo certbot renew --cert-name phu73l.net --dns-digitalocean --dns-digitalocean-credentials conf/certbot-creds.ini

- add expiration to calendar, "sudo certbot certificates" to show the date
- sudo cat /etc/letsencrypt/live/phu73l.net/cert.pem /etc/letsencrypt/live/phu73l.net/chain.pem /etc/letsencrypt/live/phu73l.net/fullchain.pem >/tmp/all.pem
- Reimport the certificate as in Import or reimport and deploy certificate

---

# Delete certificates

This does not normally have to be done.

- certbot certificates
- certbot delete --cert-name dev.dialplans.phu73l.net
- visit ACM web console

# List certificates

- certbot certificates
- visit AWS ACM web console
- change region to us-east-1


# Test

Run the itest tests, or POST to a smoke test URL, as described in test.md.

# Notes

The box that certbot is run on stores the creds and becomes a local registry for the certs, when we register on create/update, Let's Encrypt sends the reminder email. Do we need the local certs stored in /etc/letsencrypt when we renew or can they be thrown away after they're in ACM?

The cert expiry is short, this process must be repeated each time. I think the usual process is to have the infrastructure and staff, a networked box running certbot and a human to keep it running? It doesn't look hard if we aren't really concerned about security, need to run it with an auth hook periodically for autorewnewal. Might be worth it to just buy 4 certs a year?

https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains-prerequisites.html
https://eff-certbot.readthedocs.io/en/stable/using.html#manual
https://aws.github.io/chalice/topics/domainname.html
