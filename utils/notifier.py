
def notify_users_in_radius(incident, firehose=True):
    client = TwilioRestClient(TWILIO_SID, TWILIO_SECRET)
    radius = 100 if firehose is True else 20

    nearby_uls = UserLocation.objects.filter(poi__point__distance_lte=(incident.location.point, D(mi=radius)))

    for user_location in nearby_uls:
        account = user_location.account
        phone_number = str(account.phone_number)
        sms_body = incident.sms_str(user_location)
        message = client.messages.create(to=phone_number, from_=TWILIO_NUMBER, body=sms_body)
        print("Sending SMS to %s: %s" % (account.user.first_name + account.user.last_name, str(account.phone_number)))

    return nearby_uls.count()
