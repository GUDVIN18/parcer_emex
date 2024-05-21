import pandas as pd

# Загрузка данных из Excel файла
df = pd.read_excel('proxy/proxy.xlsx')

# Сохранение данных из первого столбца в список
proxies_list = df.iloc[:, 0].tolist()

# Формирование строки для переменной
proxies = "proxies = [\n"
proxies += ",\n".join(f'    "{proxy}"' for proxy in proxies_list)
proxies += "\n]"

# Вывод переменной
print(proxies)
