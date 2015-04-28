"""
TODO: Add to use proper Exception catching when charging cards
"""

try:
  # Use Stripe's bindings...
  pass
except stripe.error.CardError, e:
  # Since it's a decline, stripe.error.CardError will be caught
  body = e.json_body
  err  = body['error']

  print "Status is: %s" % e.http_status
  print "Type is: %s" % err['type']
  print "Code is: %s" % err['code']
  # param is '' in this case
  print "Param is: %s" % err['param']
  print "Message is: %s" % err['message']
except stripe.error.InvalidRequestError, e:
  # Invalid parameters were supplied to Stripe's API
  pass
except stripe.error.AuthenticationError, e:
  # Authentication with Stripe's API failed
  # (maybe you changed API keys recently)
  pass
except stripe.error.APIConnectionError, e:
  # Network communication with Stripe failed
  pass
except stripe.error.StripeError, e:
  # Display a very generic error to the user, and maybe send
  # yourself an email
  pass
except Exception, e:
  # Something else happened, completely unrelated to Stripe
  pass