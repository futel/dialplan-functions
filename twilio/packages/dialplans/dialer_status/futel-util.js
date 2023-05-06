// Return a string corresponding to our environment eg 'dev', 'prod'
function getEnvironment(context) {
    return 'stage';  // XXX we are stage!
}

// Return an extension extracted from sipUri, or null.
function sipToExtension(sipUri) {
    const regExSipUri = /^sip:((\+)?.*)@(.*)/;
    if (!sipUri.match(regExSipUri)) {
        console.log("Could not parse appropriate extension from SIP URI.");
        return null;
    }
    return decodeURIComponent(sipUri.match(regExSipUri)[1]);
}

// Return an extension for E.164 string.
function e164ToExtension(e164, extensionMap) {
    for (key in extensionMap) {
        if (extensionMap[key].callerId == e164) {
            return key;
        }
    }
    console.log("Could not find extension for E.164 number");
    return null;
}

exports.getEnvironment = getEnvironment;
exports.sipToExtension = sipToExtension;
exports.e164ToExtension = e164ToExtension;
