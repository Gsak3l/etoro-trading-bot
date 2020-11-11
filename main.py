import multiprocessing
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

manager = multiprocessing.Manager()
stock_info = manager.list()
stocks_to_buy = manager.list()
flags = manager.list()


# noinspection PyBroadException
class Auto_trading_bot:
    def __init__(self):
        # chrome 86 driver, you might have to install a different file here
        opts = Options()
        # changing user-agent because etoro detects the automated browser somehow
        opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.183 Safari/537.36")
        self.bot = webdriver.Chrome(executable_path='./chromedriver', options=opts)

    def get_stock_info(self, local_stock_info):
        bot = self.bot
        bot.get('https://finance.yahoo.com/most-active')  # reaching the site
        buttons = bot.find_elements_by_tag_name('button')  # getting all the buttons
        for button in buttons:
            if button.get_attribute('value') == 'agree':
                button.click()  # clicking the consent button
                break  # breaking the loop (or the if, I am not sure)
        # clicking twice the % change on the stocks table
        for i in range(2):
            time.sleep(3)  # waiting for the table content to load
            bot.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/'
                                      'div[2]/div[1]/table/thead/tr/th[5]').click()
        time.sleep(5)
        # getting the entire table
        table = bot.find_element_by_tag_name('tbody')
        # getting all the rows
        rows = table.find_elements_by_tag_name('tr')
        for row in rows:
            # getting the first column for each row, the name of the stock
            stock_names = row.find_elements_by_tag_name('td')[0].text  # stock names
            stock_per_change = row.find_elements_by_tag_name('td')[4].text  # stock percentage change
            stock_volume = row.find_elements_by_tag_name('td')[5].text  # stock total volume
            try:
                stock_per_change = stock_per_change.split('+', 1)[1]  # getting the numbers and not the +
            except:
                stock_per_change = "-10.1"  # we don't need negative values
            stock_per_change = stock_per_change.split('.', 1)[0]  # not getting decimal
            stock_volume = stock_volume.split('.', 1)[0]  # getting only the millions and not the thousands
            stock_per_change = int(stock_per_change)  # converting to integer
            stock_volume = int(stock_volume)  # converting to int
            # calculating the buying value
            buying_value = (3 * stock_per_change + 2 * stock_volume) % 5
            # appending the array's row
            local_stock_info.append([stock_names, stock_per_change, stock_volume, buying_value])
        flags.append(True)
        bot.close()  # shuts down the bot

    def buy_stocks(self, email, password):
        bot = self.bot
        bot.get('https://www.etoro.com/login')  # accessing the etoro website
        form = bot.find_element_by_tag_name('form')  # finding the form
        inputs = form.find_elements_by_tag_name('input')  # getting all the inputs available in the form
        # filling the form with the email and password
        inputs[0].send_keys(email)
        inputs[1].send_keys(password)
        # sleeping for a while before clicking the sign in button
        time.sleep(5)
        # clicking the sign in button
        bot.find_element_by_xpath('//button[@automation-id="login-sts-btn-sign-in"]').click()
        time.sleep(30)  # you are supposed to somehow change your ip now
        # clicking the sign in button again
        bot.find_element_by_xpath('//button[@automation-id="login-sts-btn-sign-in"]').click()
        # waiting to get the calculated values from calculate_what_to_buy
        while len(flags) != 2:
            continue
        bot.close()  # shuts down the bot

    def calculate_what_to_buy(self, local_stocks_to_buy, amount_of_money):
        bot = self.bot
        # waiting to retrieve the data from the get_stocks_info function
        while len(flags) == 0:
            continue
        stock_info_2 = sorted(stock_info, key=lambda x: x[3])
        for i in stock_info_2:
            print(i)


if __name__ == '__main__':
    bot1 = Auto_trading_bot()
    bot2 = Auto_trading_bot()
    bot3 = Auto_trading_bot()
    process1 = multiprocessing.Process(target=bot1.get_stock_info, args=(stock_info,))
    process2 = multiprocessing.Process(target=bot2.calculate_what_to_buy, args=(stocks_to_buy, 1500))
    process3 = multiprocessing.Process(target=bot2.buy_stocks, args=("email address goes here", "password goes here"))
    process1.start()
    process2.start()
    process1.join()
    process2.join()
