import requests
from bs4 import BeautifulSoup
import json
from matplotlib import pyplot as plt
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def check_beginning(tab, n):
    if tab[n] > tab[n-1]:
        return 'increasing', n
    elif tab[n] < tab[n-1]:
        return 'decreasing', n
    else:
        check_beginning(tab, n-1)


def monotonicity(mono, start_index, tab):
    if mono == 'increasing':
        while (start_index > 0) and (tab[start_index] >= tab[start_index-1]):
            start_index -= 1
        mono = 'decreasing'
        return mono, tab[start_index], start_index
    else:
        while (start_index > 0) and (tab[start_index] <= tab[start_index-1]):
            start_index -= 1
        mono = 'increasing'
        return mono, tab[start_index], start_index


def check_trend(current_trend, tab):
    repetition, index = 1, 1
    if current_trend == 'uptrend':
        while (index < len(tab) - 2) and (tab[index] >= tab[index + 2]):
            repetition += 1
            index += 1
        if tab[index] < tab[index + 1]:
            return index, repetition
        else:
            return index + 1, repetition
    elif current_trend == 'downtrend':
        while (index < len(tab) - 2) and (tab[index] <= tab[index + 2]):
            repetition += 1
            index += 1
        if tab[index] > tab[index + 1]:
            return index, repetition
        else:
            return index + 1, repetition
    else:
        return 0, 0


class CurrencyTrendChecker:

    def __init__(self):
        ctk.set_default_color_theme('dark-blue')

        self.root = ctk.CTk()
        self.root.geometry('1000x1000')

        self.root.title('Currency trend checker')

        self.upper_frame = ctk.CTkFrame(master=self.root, height=500, fg_color='white')
        self.upper_frame.pack(pady=20, padx=60, fill='both', expand=True)

        self.bottom_frame = ctk.CTkFrame(master=self.root, height=50, fg_color='transparent')
        self.bottom_frame.pack(pady=20, padx=60, fill='both', expand=True)

        self.label1 = ctk.CTkLabel(master=self.bottom_frame, text='Choose a currency')
        self.label1.pack(pady=12, padx=10)
        self.label1.place(relx=0.5, rely=0.2, anchor='center')

        self.choice = tk.StringVar()
        self.currency_choice = ctk.CTkOptionMenu(master=self.bottom_frame, variable=self.choice,
                                                 values=['USD', 'EUR', 'GBP', 'CZK', 'AUD', 'HUF'],
                                                 command=self.plot)
        self.currency_choice.pack(padx=20, pady=10)
        self.currency_choice.set('USD')
        self.currency_choice.place(relx=0.5, rely=0.6, anchor='center')
        self.choice.set('USD')

        self.root.mainloop()

    def plot(self, currency='USD'):
        url = 'https://api.nbp.pl/api/exchangerates/rates/A/{}/last/100?format=json'.format(currency)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')

        site_json = json.loads(soup.text)
        dates = []
        values = []

        for records in site_json['rates']:
            dates.append(records['effectiveDate'])
            values.append(records['mid'])

        i = len(values) - 1
        significant_values = []
        significant_indexes = [i]

        significant_values.append(values[i])

        mon, i = check_beginning(values, i)
        mon1 = mon

        while i >= 1:
            mon, significant_value, significant_index = monotonicity(mon, i, values)
            significant_values.append(significant_value)
            significant_indexes.append(significant_index)
            i = significant_index

        if 0 not in significant_indexes:
            significant_indexes.append(0)
            significant_values.append(values[0])

        if mon1 == 'increasing':
            if significant_values[1] > significant_values[3]:
                trend = 'uptrend'
            elif significant_values[1] < significant_values[3] and (significant_values[0] < significant_values[1]):
                trend = 'downtrend'
            else:
                trend = None
        else:
            if significant_values[1] > significant_values[3] and (significant_values[0] > significant_values[2]):
                trend = 'uptrend'
            elif significant_values[1] < significant_values[3]:
                trend = 'downtrend'
            else:
                trend = None

        start_date_index, iterations = check_trend(trend, significant_values)
        trend_start = dates[significant_indexes[start_date_index]]

        fig = plt.figure(figsize=(5, 5))

        x = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
        plt.plot_date(x, values, linestyle='solid')

        if iterations <= 2:
            plt.figtext(0.5, 0.01, "{} aktualnie nie znajduje sie w zadnym trendzie".format(currency), ha='center')
        elif trend == 'uptrend':
            plt.figtext(0.5, 0.01, "{} znajduje sie w uptrendzie od {}".format(currency, trend_start), ha='center')
            plt.axvline(x=x[significant_indexes[start_date_index]], color='red', linestyle='--', label='Start of the uptrend')
            plt.legend(bbox_to_anchor=(1.0, 1), loc='upper right', framealpha=1)
        else:
            plt.figtext(0.5, 0.01, "{} znajduje sie w downtrendzie od {}".format(currency, trend_start), ha='center')
            plt.axvline(x=x[significant_indexes[start_date_index]], color='blue', linestyle='--', label='Start of the downtrend')
            plt.legend(bbox_to_anchor=(1.0, 1), loc='upper right', framealpha=1)

        plt.gcf().autofmt_xdate()
        plt.title('Cena {} na przestrzeni ostatnich 100 dni'.format(currency))

        canvas = FigureCanvasTkAgg(fig, master=self.upper_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
        canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor='center')


if __name__ == '__main__':
    CurrencyTrendChecker()
