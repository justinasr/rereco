from core.model.model_base import ModelBase


class CampaignTicket(ModelBase):

    _ModelBase__schema = {
        # Database id (required by CouchDB)
        '_id': '',
        # Document revision (required by CouchDB)
        '_rev': '',
        # PrepID
        'prepid': '',
        # Name of campaign that was used as template for requests
        'campaign_name': 0.0,
        # List of input dataset names
        'input_datasets': '',
        # Processing string for this ticket
        'processing_string': '',
        # List of prepids of requests that were created from this ticket
        'created_requests': '',
        # User notes
        'notes': '',
        # Action history
        'history': []}

    __lambda_checks = {
        'prepid': lambda prepid: ModelBase.matches_regex(prepid, '[a-zA-Z0-9]{1,50}'),
        'campaign_name': lambda campaign_name: ModelBase.matches_regex(campaign_name, '[a-zA-Z0-9]{1,50}'),
        'processing_string': lambda ps: ModelBase.matches_regex(ps, '[a-zA-Z0-9_]{1,100}'),
    }

    def __init__(self, json_input=None):
        ModelBase.__init__(self, json_input)

    def check_attribute(self, attribute_name, attribute_value):
        if attribute_name in self.__lambda_checks:
            return self.__lambda_checks.get(attribute_name)(attribute_value)

        return True