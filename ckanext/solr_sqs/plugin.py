from ckan.common import config

import boto3

import ckan.plugins as p


def _send_message(msg):
    client = boto3.client('sqs', 'us-east-1')
    sqs_url = config.get('ckan.sqs_solr_sync_queue_url')

    client.send_message(
        QueueUrl=sqs_url,
        MessageBody=msg
    )

class SolrSqsPlugin(p.SingletonPlugin):
    p.implements(p.IPackageController, inherit=True)

    def after_create(self, context, pkg_dict):
        _send_message(pkg_dict['id'])

    def after_update(self, context, pkg_dict):
        _send_message(pkg_dict['id'])

    def after_delete(self, context, pkg_dict):
        _send_message(pkg_dict['id'])
