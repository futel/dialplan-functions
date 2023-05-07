// Functions to publish metric events to SNS.

const { SNSClient, PublishCommand } = require("@aws-sdk/client-sns");

const futelUtil = require('./futel-util');
const metricHostBase = 'twilio-sip-server';

// Return the appropriate metric event hostname for our environment.
function getMetricHostname(context) {
    return metricHostBase + '-' + futelUtil.getEnvironment(context);
}

function eventToMessage(context, event) {
    let dateString = new Date().toISOString();
    // PJSIP is an implementation detail from Asterisk that the usage grapher might require?
    //let channelString = "PSJIP/" + event.Channel;
    event = {
        Event: 'UserEvent',
        Channel: event.Channel,
        UserEvent: event.UserEvent
    };
    message = {
        timestamp: dateString,
        hostname: getMetricHostname(context),
        event: event};
    return JSON.stringify(message);
}

// Return a config object populated from environment.
function getConfig() {
    return {
        region: 'us-west-2',
        credentials: {
            accessKeyId: process.env.AWS_ACCESS_KEY_ID,
            secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY}};
}

// Return a publish parameters object populated from environment and message.
function getPublishParams(message) {
    return {
        Message: message,
        TopicArn: process.env.AWS_TOPIC_ARN
    };
}

// Return a Promise with the response from publishing the event to SNS.
function publish(context, event, topic_arn) {
    message = eventToMessage(context, event);
    const client = new SNSClient(getConfig());
    const command = new PublishCommand(getPublishParams(message));
    return client.send(command);
}

exports.publish = publish;

