
# My Notes, Being new to Django, and pretty rusty to building websites from scratch, I had to do alot of googling

# Jquery 
https://stackoverflow.com/questions/12031825/how-to-set-up-django-website-with-jquery 

# Websockets tutorial here, but out of date, broke my install!
https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django
# Actual docs more up to date, follow this
https://channels.readthedocs.io/

# Reconnecting websocket project
https://github.com/joewalnes/reconnecting-websocket


###########################################
# Original project spec below from here:
https://github.com/Yobota/connect4casestudy

# Yobota development case study

This repo contains the source code for the Yobota case study exercise.

## The exercise
We'd like you to write a web-app to play Connect 4. 
The rules of the game can be found here, if you're not familiar with them: <http://www.wikihow.com/Play-Connect-4>

We have provided a settings module, models and basic url configs. 
The codebase is small and straightforward, so we've not really commented
it much. If you have questions, shoot us a mail (see below) 

We'd like you to write the views, the templates (in Django templating 
or Jinja2 if you prefer), as well as any javascript and CSS you need.

The app should satisfy the following:

- players must login (or sign up). We have setup `django.contrib.auth` for convenience, 
but you may use other services if you wish

- once logged in, a user should land on the `games` view. Here, they should:
    - see a list of the games they are currently playing, 
    - see a list of the games they can join-up for (ie created by another user)
    - have the option to create a new `Game`
        - when a `Game` is created, other users should be able to see it in their join-up lists (see previous point)  
    - see their concluded games 

- If a user opts to join a game or make a move in a game they are playing, then they should land onto the `play` view.
this must satisfy the following:
    - a full connect 4 board is rendered using javascript and HTML; preferably styled using your CSS
    - each player is given a colour for their coins 
    - the user can make the following interactions:
        - make move (ie drop a coin into a given vertical)
        - review previous move
    - the game state should be saved via the `Game` and `Coin` models provided
    - any illegal moves should be rejected
    - something *cool* should happen when the game concludes (eg splash message on win / lose / draw; your call, go nuts.)
    - explain how you're using sessions, what have you done to keep things secure?
    - explain how you're using AJAX, what have you done to keep things secure

- for bonus points,  
    - make the game lovely to play
    - use websockets for live updates on the page
    - update the settings file to use a postgres db backend (rather than sqlite as at present)
    - make other changes as needed to support a clean deployment onto Heroku
    - write clean, readable code; with comments and tests as appropriate


## Guidelines
If there is something broken in the code we're providing, then please let us know. 

You should give yourself up to 6 hours to complete it. Once completed,
please commit to a public git and email us the link at <hello@yobota.xyz>

Feel free to use jQuery, CSS bootstraps, font awesome, or anything else you feel is reasonable or sensible. 

Make any improvements you think are necessary to our model


## Things you shouldn't do 
Please don't cheat, or use an existing implementation. We want to get to know the real you.

Don't suffer in silence, if you have questions or are genuinely stuck, give us a shout.

 
## Questions
Any questions, please email <hello@yobota.xyz>

