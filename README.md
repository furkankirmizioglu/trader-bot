
# TraderBot

As the Warren Buffett said: "If you don't find a way to make money while you sleep, you will work until you die."

Welcome to TraderBot: an algorithmic trading application developed in Python. Designed to seize trading opportunities 24/7, TraderBot operates autonomously while you focus on other aspects of your life. It adeptly navigates both the spot and futures markets on Binance, ensuring you never miss a chance to capitalize on potential gains. This cutting-edge solution is hosted on a Raspberry Pi 4, serving as a reliable local server.

With every executed order, TraderBot keeps you informed. It promptly sends push notifications and tweets to ensure you're always in the trade. Stay updated by following our Twitter account, [TraderBotStatus](https://twitter.com/traderbotstatus).

In the unlikely event of an exception during runtime, TraderBot remains proactive. It promptly sends detailed exception logs via email to designated administrators (currently, this function is directed to me 🙃).

Welcome to algorithmic trading world, this is your trend follower friend.

## Screenshots

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/0f77098e-eabb-454f-893c-c1872bfc0508)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/72c87a9e-cab4-45ac-bd92-14fe10a270f0)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/f03c82a1-4568-46ef-9410-4ded786e31c5)

![App Screenshot](https://github.com/furkankirmizioglu/trader-bot/assets/29805446/43014a12-dac1-4dae-84a3-1982a0b9a8a7)


## Features

- Trades on Binance, both spot & futures markets on designated parities.
- Real-time Twitter account.
- Sends push notification through Google Firebase via Android mobile app.
- Exception handling & alert mechanism.


## Tech Stack

**Server:** 
- Python
- Firebase Cloud Messaging

**Physical:** Raspberry Pi 4 Model B

