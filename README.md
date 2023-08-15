# DiscordWebscraper
DiscordWebscraper


Ok so this is kinda doable but I have managed to get a working version atm so going to stop here with this version. 

Currently the issue is that you cannot generate a user auth token through the api. This has to be done via logging in and I have no intention of doing something as dumb as trying to login to Discord via an API request like that to get my account banned. Seems really dumb. What I can do though, is keep a webbrowser open permanantly and basically as long as that browser is alive, Discord will constantly refresh that user auth token, meaning that I can just feed one auth token in and forever keep the browser alive and be able to just scrape data for as long as I want.

