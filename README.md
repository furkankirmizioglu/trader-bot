
# TraderBot

“If you don't find a way to make money while you sleep, you will work until you die.” - Warren Buffett

TraderBot is a Python based algorithmic trading application. It looks to trade opportunities for 24/7, makes trades while you're working or sleeping. It trades on Binance, both spot and futures markets. It runs on Raspberry Pi 4 as a local server. 

When an order is placed, it sends push notification and tweet to inform user. You can follow our Twitter account (https://twitter.com/traderbotstatus)

If an exception occur while application is running, it sends an e-mail includes exception details to admins. (Currently only to me. 🙃)



## Screenshots

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/0f77098e-eabb-454f-893c-c1872bfc0508)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/72c87a9e-cab4-45ac-bd92-14fe10a270f0)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/f03c82a1-4568-46ef-9410-4ded786e31c5)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/43014a12-dac1-4dae-84a3-1982a0b9a8a7)


## Features

- Trading on spot & futures market.
- Integration with Twitter.
- Sends push notification through Google Firebase via Android mobile app.
- Exception handling & alert mechanism.


## Tech Stack

**Server:** Python, Google Firebase

**Physical:** Raspberry Pi Model 4/B

