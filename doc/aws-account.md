# How to create an AWS console user, using existing AWS CLI creds

This is not a root user even though it is called "testroot".

- Does this give every needed permission? There are errors in the console. Does this user need to be promoted to an org owner or something?
- Can this user create an access key to use for CLI creds?
- Can this user add new users in the console or CLI?

account:GetAccountInformation and billing:GetSellerOfRecord

# Create user and group

aws iam create-user \
--user-name testroot

# XXX just use the existing administrator group?

aws iam create-group \
--group-name testrootgroup

# Attach policy to group. This policy should give root access in console and cli?

aws iam attach-group-policy \
--policy-arn arn:aws:iam::aws:policy/PowerUserAccess \
--group-name testrootgroup
aws iam attach-group-policy \
--policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
--group-name testrootgroup

# Add user to group

aws iam add-user-to-group \
--user-name testroot \
--group-name testrootgroup

# An alternative is to attach the policy to the user?
# aws iam attach-user-policy \
# --policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
# --user-name testroot

# Add password to user. This allows console login.
# The console login url is then
# https://<id>.signin.aws.amazon.com/console
# To find the ARN, which contains the 12 digit account ID:
# aws iam list-users|cat
# eg
# https://168594572693.signin.aws.amazon.com/console

aws iam create-login-profile \
--user-name testroot \
--password <password>

# Notes

https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html
https://awscli.amazonaws.com/v2/documentation/api/2.4.19/reference/iam/index.html#cli-aws-iam
