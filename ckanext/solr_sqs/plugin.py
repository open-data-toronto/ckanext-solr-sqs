from ckan.common import config
import ckan.plugins.toolkit as tk

import boto3
import re

import ckan.plugins as p

@tk.side_effect_free
def send_message_api(context, data_dict):
    # make sure an authorized user is making this call
    assert context["auth_user_obj"], "This endpoint can be used by authorized accounts only"

    _send_message(data_dict["package_id"])
    return data_dict

def _send_message(msg):
    sqs_url = config.get('ckan.sqs_solr_sync_queue_url')
    region = re.search("sqs.(.*).amazon", sqs_url).group(1) 
    client = boto3.client('sqs', region)

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


    p.implements(p.IActions)
    def get_actions(self):
        return {
            "solr_reindex_message": send_message_api
        }
