

import re


class Adapter(object):
    """
    All adapters produce the following dictionary with the following keys:

    unit, location, intersection, venue, incident, dispatch_time
    """


class UC911Twitter(Adapter):

    def __call__(self, payload):
        """
        Using configurable incident data fields, parse the data into incident models with all of the information required.

        JADS/ Unit:TWTR Inc:Stable Loc:91 WASHINGTON AV XSts:DIVISION/MAIN Venue:Saugerties 08/07/2017 13:31
        """

        keys = {'Unit', 'Loc', 'XSts', 'Venue', 'Inc'}
        joined_keys = '|'.join(re.escape(key) for key in keys)
        key_re = re.compile(f'({joined_keys}):', re.IGNORECASE)
        key_locations = key_re.split(payload)[1:]

        incident_dict = {k.lower(): v.strip() for k, v in zip(key_locations[::2], key_locations[1::2])}

        regex = re.compile('''
                           ([a-zA-Z_\s]*)
                           ([^a-zA-Z]*)$
                           ''', re.VERBOSE)

        s = regex.search(incident_dict["venue"])

        if s.groups()[1]:
            # Adding a key to the dictionary here.
            incident_dict['dispatch_time'] = parser.parse(s.groups()[1])
            incident_dict['venue'] = str.rstrip(s.groups()[0])

            # TODO
            # if "out of" in incident_dict["venue"].lower():
            #     incident_dict["venue"] = ""
            #     # Handle out of City Dispatches here.

        else:
            pattern = re.compile('[^a-zA-Z]')
            clean_venue = pattern.sub(" ", incident_dict['Venue']).strip()
            incident_dict['Venue'] = clean_venue

        return incident_dict
