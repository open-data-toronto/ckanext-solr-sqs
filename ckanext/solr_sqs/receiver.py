from ConfigParser import ConfigParser

import subprocess
import re

import boto3


def get_url():
    config = ConfigParser()
    config.read('/etc/ckan/default/production.ini')

    return config.get('app:main', 'ckan.sqs_solr_sync_queue_url')

def receive_messages():
    sqs_url = get_url()
    region = re.search("sqs.(.*).amazon", sqs_url).group(1) 
    client = boto3.client('sqs', region)

    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get('Messages', [])

    if len(messages):
        subprocess.call([
            'paster',
            '--plugin=ckan',
            'search-index',
            'rebuild',
            '-r',
            '--config=/etc/ckan/default/production.ini'
        ])

    for m in messages:
        client.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=m['ReceiptHandle']
        )

if __name__ == '__main__':
    receive_messages()
