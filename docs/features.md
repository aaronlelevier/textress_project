# Features

High level feature highlights, that will be shared when making sales pitches.

I will be removing the inital notes from "todo's / bugs" and adding the 
new features here.


## Database

Change all IDs to UUIDs

Refactor Model inheritance


## UI

#### Forms

Red asterisk for `required`

Client side validation

#### Payment

Credit card - auto put spaces after every 4 digits for easier reading of the c.card number

### Guests

Auto-hiding of checked-out Guests


### Auto Replies

Guest (for auto-reply), can send an lowercase or uppercase letter for an auto-reply.
ex: 'h', 'H'.  These auto-replies are configured at the Hotel level.

Unread messages pop on screen

Counts of unread and total messages

Guest with unread messages show first

** Check-in ** Message hook - for use with a "Welcome" message for example


### USERS

-Add a FormSet, so that Mgrs' can in the same view adjust
    Group Status to "hotel_manager" or take it away.

- also be able to view Group.


### VENDOR

- do package upgrades to 'angular' packages
- put their versions in 'packages.json'
- remove the /vendor/ folder from version control
