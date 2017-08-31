from adapters.ulster_ny import UC911Twitter


ADAPTERS = {
    ('UlsterCounty911', 'twitter'): UC911Twitter
}


def adapter_selector(incident_data):
    """
    Identifies agency, retrieves proper parser by source, then
    send payload into the adapter.
    """
    identifier = (incident_data['agency'], incident_data['source'])
    adapter = ADAPTERS[identifier]()    # Instantiate
    return adapter