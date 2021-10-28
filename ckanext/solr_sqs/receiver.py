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

    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get("Messages", [])

    if len(messages):
        subprocess.call(
            [
                "ckan",
                "--config=/etc/ckan/default/production.ini",
                "search-index",
                "rebuild",
                "-r",
            ]
        )

    for m in messages:
        client.delete_message(QueueUrl=sqs_url, ReceiptHandle=m["ReceiptHandle"])


if __name__ == "__main__":
    receive_messages()
