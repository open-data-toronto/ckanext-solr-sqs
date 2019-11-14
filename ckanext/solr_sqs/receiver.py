from ckan.common import config

import boto3

client = boto3.client('sqs', 'us-east-1')
sqs_url = config.get('ckan.sqs_solr_sync_queue_url')

print(sqs_url)

def _receive_messages():
    response = client.receive_message(QueueUrl=url, MaxNumberOfMessages=10)
    messages = response.get('Messages', [])

    for message in messages['Messages']:
        client.delete_message(
            QueueUrl=url,
            ReceiptHandle=message['ReceiptHandle']
        )

if __name__ == '__main__':
    _receive_messages()
