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
    # so we fetch the sqs messages 10 at a time until there are none left
    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get("Messages", [])

    if len(messages):
        # Before looping through all messages, refresh the whole solr index once for good measure
        subprocess.call(
            [
                "ckan",
                "--config=/etc/ckan/default/production.ini",
                "search-index",
                "rebuild",
                "-r"
            ])

    while len(messages) > 0:
            
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
                    message["Body"]
                ]
            )
            # delete the message from the queue
            client.delete_message(QueueUrl=sqs_url, ReceiptHandle = message["ReceiptHandle"]) 
        
        # fetch the next batch of messages and start the cycle again
        response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
        messages = response.get("Messages", [])
            
# this function gets called directly by cron, hence the if __name__ == "__main__"
if __name__ == "__main__":
    receive_messages()
