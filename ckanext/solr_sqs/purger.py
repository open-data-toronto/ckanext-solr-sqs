import re
import subprocess
from configparser import ConfigParser

import boto3


def get_url():
    config = ConfigParser()
    config.read("/etc/ckan/default/production.ini")

    return config.get("app:main", "ckan.sqs_solr_sync_queue_url")


def purge_messages():
    # this script is solely intended to purge all messages in this environment's SQS queue
    sqs_url = get_url()
    region = re.search("sqs.(.*).amazon", sqs_url).group(1)
    client = boto3.client("sqs", region)

    # purge messages
    client.purge_queue(QueueUrl = sqs_url)

    # ensure the purge worked
    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get("Messages", [])
    assert len(messages) == 0, "Queue still has {} messages in it after purge".format(len(messages))

# this function gets called directly, hence the if __name__ == "__main__"
if __name__ == "__main__":
    purge_messages()
