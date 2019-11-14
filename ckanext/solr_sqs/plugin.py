from ckan.common import config

import boto3

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import logging
logger = logging.getLogger('ckan.base.logic')

def _send_message(msg):
    client = boto3.client('sqs', 'us-east-1')

    sqs_url = config.get('ckan.sqs_solr_sync_queue_url')

    client.send_message(
        QueueUrl=sqs_url,
        MessageBody=msg
    )

class SolrSqsPlugin(plugins.SingletonPlugin):
    p.implements(p.IPackageController, inherit=True)

    def after_create(context, pkg_dict):
        logger.warn(('create', pkg_dict['id']))
        _send_message(pkg_dict['id'])

    def after_update(context, pkg_dict):
        logger.warn(('update', pkg_dict['id']))
        _send_message(pkg_dict['id'])

    def after_delete(context, pkg_dict):
        logger.warn(('delete', pkg_dict['id']))
        _send_message(pkg_dict['id'])
