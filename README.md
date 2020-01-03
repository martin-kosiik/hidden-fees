# Comparing hidden fees for currency exchange
This is a repository of a project for the course [Data Processing in Python](https://github.com/vitekzkytek/PythonDataIES).

The application downloads exchange rates offered by 10 Central European banks (Česká spořitelna, Komerční banka, ČSOB, Raiffeisenbank, Fio banka, 
mBank, Slovenská sporiteľňa, VÚB banka, Tatra banka, and OTP Bank). The data are analysed and visualized. Furthermore, we created an interactive application that compares the hidden fees for a chosen currency route. A hidden fee is a fee arising from a currency exchange where the exchange rate is not equal to a mid-market exchange rate.

A script `downloaddata.py` was downloading bank and market exchange rates every day at 8:00 AM for a period of more than a month in order to create panel data saved in files `bank_rates.csv` and `market_rates.csv`.
