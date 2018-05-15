/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event The Cloud Functions event.
 * @param {!Function} The callback function.
 */
const request = require('retry-request');
const fs = require('fs');
const Storage = require('@google-cloud/storage');
const pubSub = require('@google-cloud/pubsub');

const projectId = "cloud-iot-testing-185623";

const extTopic = "iot-cloud-topic";
const extProjectId = "gcp-io-demo";
//const extCloudRegion = "us-central1";
//const extRegistryId = "iot-cloud-registry";
//const extDeviceId = "iot-cloud-device";
const messageType="events"
const maxMessages = 100;
const algorithm = "RS256";
const maxWaitTime = 2000;
//const extTopicName = `/devices/${extDeviceId}/events`;

const storage = new Storage({
  projectId: projectId,
});

var bucket = storage.bucket('dataflow-cloud-iot-testing-185623');
var file = bucket.file('PemFiles/gcp-io-demo-f9169e6dd7ab.json');

//const httpBridgeAddress = "cloudiotdevice.googleapis.com";
//const topicName = `projects/${extProjectId}/locations/${extCloudRegion}/registries/${extRegistryId}/devices/${extDeviceId}`;

// The request path, set accordingly depending on the message type.
const pathSuffix = messageType === 'events' ? ':publishEvent' : ':setState';
//const urlBase = `https://${httpBridgeAddress}/v1/${topicName}`;
//const url = `${urlBase}${pathSuffix}`;
// [END iot_http_variables]

function publishMessage(pubsubClient, topicName, data) {
  // [START pubsub_publish_message]
  // Imports the Google Cloud client library

  /**
   * TODO(developer): Uncomment the following lines to run the sample.
   */
  // const topicName = 'your-topic';
  // const data = JSON.stringify({ foo: 'bar' });

  // Publishes the message as a string, e.g. "Hello, world!" or JSON.stringify(someObject)
  const dataBuffer = Buffer.from(data);

  pubsubClient
    .topic(topicName)
    .publisher({
    batching: {
      maxMessages: 100,
      maxMilliseconds: 20000,
    },
  })
    .publish(dataBuffer)
    .then(messageId => {
      console.log(`Message ${messageId} published.`);
    })
    .catch(err => {
      console.error('ERROR:', err);
    });
  // [END pubsub_publish_message]
}

exports.subscribe = (event, callback) => {
  file.download({
    destination: '/tmp/gcp-io-demo-f9169e6dd7ab.json'
    }, function(err) {
    const pubsubMessage = event.data;
	var data = Buffer.from(pubsubMessage.data, 'base64').toString();
    const pubsubClient = pubSub({
    projectId: extProjectId,
    keyFilename: '/tmp/gcp-io-demo-f9169e6dd7ab.json'
    });
    publishMessage(pubsubClient, extTopic, data); 
  });

};

