from ConfigParser import ConfigParser

import subprocess

import boto3


def get_url():
    config = ConfigParser()
    config.read('/etc/ckan/default/production.ini')

    return config.get('app:main', 'ckan.sqs_solr_sync_queue_url')

def receive_messages():
    client = boto3.client('sqs', 'us-east-1')
    sqs_url = get_url()

    response = client.receive_message(QueueUrl=sqs_url, MaxNumberOfMessages=10)
    messages = response.get('Messages', [])

    processed = []

    for m in messages:
        pid = m['Body']

        if not pid in processed:
            subprocess.call([
                'paster',
                '--plugin=ckan',
                'search-index',
                'rebuild',
                pid,
                '--config=/etc/ckan/default/production.ini'
            ])

            processed.append(pid)

        client.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=m['ReceiptHandle']
        )

if __name__ == '__main__':
    receive_messages()
