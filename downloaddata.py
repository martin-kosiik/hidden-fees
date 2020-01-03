# pip install --upgrade numpy pandas matplotlib jupyter requests scrapy
# 0 8 * * * /bin/bash -c "source $HOME/env/bin/activate && cd $HOME/download && python $HOME/download/downloaddata.py &>> $HOME/download/download.log"

import numpy as np
import pandas as pd
import requests
import datetime
from scrapy import Selector

class Compare:
    # Fill `bank_rates` and `market_rates` data frames with data
    def __init__(self):
        # Download bank exchange rates into `bank_rates`
        date = datetime.date.today()
        self.bank_rates = []
        self.download_ceska_sporitelna()
        self.download_komercni_banka()
        self.download_csob()
        self.download_raiffeisenbank()
        self.download_fio_banka()
        self.download_mbank()
        self.download_slovenska_sporitelna(date)
        self.download_vub_banka()
        self.download_tatra_banka(date)
        self.download_otp_bank(date)

        # Create a data frame from `bank_rates`
        self.bank_rates = pd.DataFrame(self.bank_rates, columns=["from", "to", "rate", "bank"])
        # Create a data frame `market_rates` with market exchange rates for each route in `bank_rates`
        self.market_rates = self.bank_rates.drop(columns=["rate", "bank"]).drop_duplicates().apply(self.download_transferwise, axis=1, result_type="expand")
        self.market_rates.columns = ["from", "to", "rate"]

    # Download exchange rates from Česká spořitelna website into `bank_rates`
    def download_ceska_sporitelna(self):
        bank_name = "Česká spořitelna"
        try:
            self.print_info_bank_downloading(bank_name)
            items = requests.get("https://api.csas.cz/webapi/api/v2/rates/exchangerates", headers={"WEB-API-key": "08aef2f7-8b72-4ae1-831e-2155d81f46dd"}).json()
            self.print_info_bank_parsing(bank_name)
            for item in items:
                currency = str(item["shortName"].strip())
                quantity = int(item["amount"])
                buy_rate = float(item["currBuy"])
                sell_rate = float(item["currSell"])
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from Komerční banka website into `bank_rates`
    def download_komercni_banka(self):
        bank_name = "Komerční banka"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.kb.cz/cs/kurzovni-listek/cs/rl/index.x?display=table").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("div#p_lt_WebPartZone6_zoneContent_contentPH_p_lt_WebPartZone2_zoneContent_ExchangeRates_ratesTablePnl a.link--black.link--no-decoration div.row")
            for item in items:
                currency = str(item.css("div.col.exchange-table__name.mr-3 strong.exchange-table__currency.exchange-table__currency-code::text").extract_first().strip())
                quantity = int(item.css("div.col.exchange-table__name.mr-3 strong.exchange-table__currency.exchange-table__currency-amount::text").extract_first().strip())
                buy_rate = float(item.css("div.col.exchange-table__value.box-shadow.d-flex.justify-content-between.mr-3:nth-of-type(4) span.exchange-table__value-inner.d-flex.align-items-center.justify-content-center:nth-of-type(1)::text").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("div.col.exchange-table__value.box-shadow.d-flex.justify-content-between.mr-3:nth-of-type(4) span.exchange-table__value-inner.d-flex.align-items-center.justify-content-center:nth-of-type(2)::text").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from ČSOB website into `bank_rates`
    def download_csob(self):
        bank_name = "ČSOB"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.csob.cz/portal/lide/kurzovni-listek").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("div.npw-row-text.pui-exchange-rates-table div.pdp-table table tbody tr")
            for item in items:
                currency = str(item.css("td.pui-currency span.npw-currency.npw-data-link-url::text").extract_first().strip())
                quantity = int(item.css("td.pui-amount span.pui-amount-with-currency::text").extract_first().strip())
                buy_rate = float(item.css("td.pui-buy span.npw-currency-type-change::attr(data-cashless)").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("td.pui-sell span.npw-currency-type-change::attr(data-cashless)").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from Raiffeisenbank website into `bank_rates`
    def download_raiffeisenbank(self):
        bank_name = "Raiffeisenbank"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.rb.cz/informacni-servis/kurzovni-listek").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("div.container table.table.responsive-accordion.th-highlight tbody tr:not(.hidden)")
            for item in items:
                currency = str(item.css("td.code::text").extract_first().strip())
                quantity = int(item.css("td.count input").attrib["value"].strip())
                buy_rate = float(item.css("td.value:nth-of-type(4)::text").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("td.value:nth-of-type(5)::text").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from Fio banka website into `bank_rates`
    def download_fio_banka(self):
        bank_name = "Fio banka"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.fio.cz/akcie-investice/dalsi-sluzby-fio/devizove-konverze").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("table.tbl-sazby tbody tr")
            for item in items:
                currency = str(item.css("td.col1:nth-of-type(1)::text").extract_first().strip())
                quantity = int(item.css("td.tright:nth-of-type(3)::text").extract_first().strip())
                buy_rate = float(item.css("td.tright:nth-of-type(4)::text").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("td.tright:nth-of-type(5)::text").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from mBank website into `bank_rates`
    def download_mbank(self):
        bank_name = "mBank"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.mbank.cz/kurzovni-listek/").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("div#currencies div.table_0 table.default tbody tr:not(.chartbox)")
            for item in items:
                currency = str(item.css("td.unit:nth-of-type(2) div::text").extract_first().strip())
                quantity = int(item.css("td:nth-of-type(4)::text").extract_first().strip())
                buy_rate = float(item.css("td:nth-of-type(5)::text").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("td:nth-of-type(6)::text").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "CZK", buy_rate / quantity, bank_name])
                self.bank_rates.append(["CZK", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from Slovenská sporiteľňa website into `bank_rates`
    def download_slovenska_sporitelna(self, date):
        bank_name = "Slovenská sporiteľňa"
        try:
            self.print_info_bank_downloading(bank_name)
            items = requests.get("https://api.slsp.sk/api/v1/fxRatesList?rateType=Exchange&currencies=USD;CZK;PLN;HRK;HUF;BGN;GBP;CHF;AUD;CAD;RUB;JPY;NOK;DKK;SEK;RON;CNY;HKD;TRY&date=" + date.isoformat()).json()["fx"]
            self.print_info_bank_parsing(bank_name)
            for item in items:
                currency = str(item["currency"].strip())
                quantity = 1
                buy_rate = float(item["exchangeRate"]["buy"])
                sell_rate = float(item["exchangeRate"]["sell"])
                if len(self.bank_rates) != 0 and self.bank_rates[-1][1] == currency and self.bank_rates[-1][3] == "Slovenská sporiteľňa":
                    self.bank_rates.pop()
                    self.bank_rates.pop()
                self.bank_rates.append([currency, "EUR", quantity / buy_rate, bank_name])
                self.bank_rates.append(["EUR", currency, sell_rate / quantity, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from VÚB banka website into `bank_rates`
    def download_vub_banka(self):
        bank_name = "VÚB banka"
        try:
            self.print_info_bank_downloading(bank_name)
            sel = Selector(text=requests.get("https://www.vub.sk/ludia/pre-kazdy-den/kurzovy-listok/").content)
            self.print_info_bank_parsing(bank_name)
            items = sel.css("table#kurz.tabulkaCennik tbody tr")
            for item in items:
                currency = str(item.css("td:nth-of-type(3)::text").extract_first().strip())
                quantity = 1
                buy_rate = float(item.css("td:nth-of-type(4)::text").extract_first().strip().replace(",", "."))
                sell_rate = float(item.css("td:nth-of-type(6)::text").extract_first().strip().replace(",", "."))
                self.bank_rates.append([currency, "EUR", quantity / buy_rate, bank_name])
                self.bank_rates.append(["EUR", currency, sell_rate / quantity, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from Tatra banka website into `bank_rates`
    def download_tatra_banka(self, date):
        bank_name = "Tatra banka"
        try:
            self.print_info_bank_downloading(bank_name)
            items = requests.get("https://www.tatrabanka.sk/rest/tatra/exchange/list/" + date.strftime("%d.%m.%Y") + "-00:00").json()
            self.print_info_bank_parsing(bank_name)
            for item in items:
                currency = str(item["feCycd"].strip())
                quantity = int(item["feAmnt"])
                buy_rate = float(item["feDnrt"])
                sell_rate = float(item["feDprt"])
                self.bank_rates.append([currency, "EUR", quantity / buy_rate, bank_name])
                self.bank_rates.append(["EUR", currency, sell_rate / quantity, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download exchange rates from OTP Bank website into `bank_rates`
    def download_otp_bank(self, date):
        bank_name = "OTP Bank"
        try:
            self.print_info_bank_downloading(bank_name)
            items = requests.get("https://www.otpbank.hu/apps/exchangerate/api/exchangerate/otp/" + date.isoformat()).json()["dates"][0]["versions"][-1]["exchangeRates"]
            self.print_info_bank_parsing(bank_name)
            for item in items:
                currency = str(item["currencyCode"].strip())
                quantity = int(item["unitSize"])
                buy_rate = float(item["foreignExchangeBuyingRate"])
                sell_rate = float(item["foreignExchangeSellingRate"])
                self.bank_rates.append([currency, "HUF", buy_rate / quantity, bank_name])
                self.bank_rates.append(["HUF", currency, quantity / sell_rate, bank_name])
        except:
            self.print_error_bank(bank_name)

    # Download market exchange rate from TransferWise website for the specified route
    def download_transferwise(self, route):
        try:
            self.print_info_market_downloading(route)
            return [route[0], route[1], float(requests.get("https://api.transferwise.com/v1/rates?source=" + route[0] +"&target=" + route[1], headers={"authorization": "Basic OGNhN2FlMjUtOTNjNS00MmFlLThhYjQtMzlkZTFlOTQzZDEwOjliN2UzNmZkLWRjYjgtNDEwZS1hYzc3LTQ5NGRmYmEyZGJjZA=="}).json()[0]["rate"])]
        except:
            self.print_error_market(route)
            return [route[0], route[1], np.nan]

    # Save `bank_rates` and `market_rates` to CSV files
    def save_data(self):
        date = datetime.date.today()
        self.bank_rates["date"] = date.isoformat()
        self.market_rates["date"] = date.isoformat()
        self.bank_rates.to_csv("bank_rates.csv", header=False, index=False, mode="a")
        self.market_rates.to_csv("market_rates.csv", header=False, index=False, mode="a")

    # Print an error message when exchange rates for a particular bank cannot be downloaded
    def print_error_bank(self, bank_name):
        print("[error " + self.formatted_time() + "] Failed to download exchange rates for " + bank_name + ".")

    # Print an error message when market exchange rate for a particular route cannot be downloaded
    def print_error_market(self, route):
        print("[error " + self.formatted_time() + "] Failed to download market exchange rate for the route " + route[0] + " → " + route[1] + ".")

    # Print a message before downloading exchange rates for a particular bank
    def print_info_bank_downloading(self, bank_name):
        print("[info " + self.formatted_time() + "] Started downloading exchange rates for " + bank_name + ".")

    # Print a message before parsing exchange rates for a particular bank
    def print_info_bank_parsing(self, bank_name):
        print("[info " + self.formatted_time() + "] Started parsing exchange rates for " + bank_name + ".")

    # Print a message before downloading market exchange rate for a particular route
    def print_info_market_downloading(self, route):
        print("[info " + self.formatted_time() + "] Started downloading market exchange rate for the route " + route[0] + " → " + route[1] + ".")

    # Return a formatted date and time string suitable for logging
    def formatted_time(self):
        return datetime.date.today().isoformat() + " " + datetime.datetime.today().time().replace(microsecond=0).isoformat()

comparenow = Compare()
comparenow.save_data()

