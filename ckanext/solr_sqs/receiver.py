import re
import subprocess
from configparser import ConfigParser

import boto3


def get_url():
    config = ConfigParser()
    config.read("/etc/ckan/default/production.ini")

    return config.get("app:main", "ckan.sqs_solr_sync_queue_url")


# receive_messages gets the messages from the SQS queue and executes the solr reindex
# This is triggered via a CRON job in the schedule: */5 * * * * /root/solrsqs.sh > /dev/null 2>&1
# The CRON job runs a bash script that effectively runs this script:
#
#!/bin/bash
# . /usr/lib/ckan/default/bin/activate
# python /usr/lib/ckan/default/src/ckanext-solr-sqs/ckanext/solr_sqs/receiver.py
#
def receive_messages():

    sqs_url = get_url()
    region = re.search("sqs.(.*).amazon", sqs_url).group(1)
    client = boto3.client("sqs", region)

    # there are a maximum of 10 messages fetched in client.receive_message
    # we only process 10 messages per run of this script because this script
    # runs every 5 minutes and we dont want to have it running multiple times
    # in parallel

    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get("Messages", [])
    print(messages)

    if len(messages):
        # Before looping through all messages, refresh the whole solr index once for good measure
        subprocess.call(
            [
                "ckan",
                "--config=/etc/ckan/default/production.ini",
                "search-index",
                "rebuild",
            ]
        )

    processed = []
    # for each message in the queue, recreate the package in the message's index
    for message in messages:
        # if we've already reindexed a package in this run, dont do it again
        if message["Body"] in processed:
            continue

        processed.append(message["Body"])

        subprocess.call(
            [
                "ckan",
                "--config=/etc/ckan/default/production.ini",
                "search-index",
                "rebuild",
                message["Body"],
            ]
        )
        # delete the message from the queue
        client.delete_message(QueueUrl=sqs_url, ReceiptHandle=message["ReceiptHandle"])


# this function gets called directly by cron, hence the if __name__ == "__main__"
if __name__ == "__main__":
    receive_messages()
