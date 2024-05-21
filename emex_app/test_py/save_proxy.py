import pandas as pd
proxies = []


def convert_proxy_format(proxy):
    # Разбиваем строку по символу '@' для отделения IP:PORT от USERNAME:PASSWORD
    ip_port, user_pass = proxy.split('@')
    
    # Далее разбиваем IP:PORT и USERNAME:PASSWORD по их разделителям
    ip, port = ip_port.split(':')
    username, password = user_pass.split(':')
    
    # Формируем новый формат URL прокси
    new_proxy_format = f"http://{username}:{password}@{ip}:{port}"
    return new_proxy_format

# Пример использования функции

old_proxy = "46.8.110.142:1050@Mxh8qs:BfMfVqqOCc"
new_proxy = convert_proxy_format(old_proxy)
print("New format:", new_proxy)


with open('proxies.txt', 'r') as file:
    for line in file:
        line = line.strip()  # Удаление пробельных символов
        if line:  # Проверка на пустую строку
            ip_port, user_pass = line.split('@')

            # Далее разбиваем IP:PORT и USERNAME:PASSWORD по их разделителям
            ip, port = ip_port.split(':')
            username, password = user_pass.split(':')
            
            # Формируем новый формат URL прокси
            new_proxy_format = f"http://{username}:{password}@{ip}:{port}"
            print(new_proxy_format)
            proxies.append(new_proxy_format)

print(proxies)
# Создание DataFrame
df = pd.DataFrame(proxies, columns=['Proxy'])

### Шаг 3: Сохранение данных в Excel файл
# Сохраняем DataFrame в Excel файл
df.to_excel('proxy/proxy.xlsx', index=False)

print("Прокси успешно сохранены в файл 'proxy.xlsx'.")










# proxies = [
    #     "http://oX52rq:RvAxW3@46.3.197.140:9069",
    #     "http://hVY2Cd:2L748V@46.3.199.136:9150",
    #     "http://hVY2Cd:2L748V@46.3.198.177:9314",
    #     "http://hVY2Cd:2L748V@46.3.197.127:9361",
    #     "http://1RzeHb:6AvjQx@194.28.209.79:9397",
    #     "http://1RzeHb:6AvjQx@194.28.209.238:9714",
    #     "http://1RzeHb:6AvjQx@194.28.209.249:9336",
    #     "http://1RzeHb:6AvjQx@194.28.208.53:9254",
    #     "http://1RzeHb:6AvjQx@194.28.210.155:9349",
    #     "http://1RzeHb:6AvjQx@194.28.210.192:9633",
    #     "http://1RzeHb:6AvjQx@194.28.209.60:9778",
    #     "http://1RzeHb:6AvjQx@194.28.210.85:9470",
    #     "http://1RzeHb:6AvjQx@194.28.211.203:9944",
    #     "http://1RzeHb:6AvjQx@194.28.210.37:9837",
    #     "http://1RzeHb:6AvjQx@194.28.210.79:9757",
    #     "http://1RzeHb:6AvjQx@194.28.210.44:9511",
    #     "http://1RzeHb:6AvjQx@194.28.209.214:9633",
    #     "http://1RzeHb:6AvjQx@194.28.209.213:9430",
    #     "http://1RzeHb:6AvjQx@194.28.210.123:9277",
    #     "http://1RzeHb:6AvjQx@194.28.210.210:9185",
    #     "http://1RzeHb:6AvjQx@194.28.208.183:9317",
    #     "http://1RzeHb:6AvjQx@194.28.209.102:9432",
    #     "http://1RzeHb:6AvjQx@194.28.211.150:9640",
    #     "http://1RzeHb:6AvjQx@194.28.208.194:9999",
    #     "http://1RzeHb:6AvjQx@194.28.208.223:9348",
    #     "http://1RzeHb:6AvjQx@194.28.209.93:9191",
    #     "http://1RzeHb:6AvjQx@194.28.211.180:9685",
    #     "http://1RzeHb:6AvjQx@194.28.209.143:9480",
    #     "http://1RzeHb:6AvjQx@194.28.210.164:9403",
    #     "http://1RzeHb:6AvjQx@194.28.208.63:9523",
    #     "http://1RzeHb:6AvjQx@194.28.210.212:9044",
    #     "http://1RzeHb:6AvjQx@194.28.211.26:9988",
    #     "http://1RzeHb:6AvjQx@194.28.210.92:9031",
    #     "http://1RzeHb:6AvjQx@212.81.39.124:9528",
    #     "http://1RzeHb:6AvjQx@212.81.36.254:9798",
    #     "http://1RzeHb:6AvjQx@212.81.38.152:9919",
    #     "http://1RzeHb:6AvjQx@212.81.36.180:9880",
    #     "http://1RzeHb:6AvjQx@212.81.39.217:9994",
    #     "http://1RzeHb:6AvjQx@212.81.39.196:9995",
    #     "http://1RzeHb:6AvjQx@212.81.39.185:9272",
    #     "http://1RzeHb:6AvjQx@212.81.39.207:9048",
    #     "http://1RzeHb:6AvjQx@212.81.39.147:9770",
    #     "http://1RzeHb:6AvjQx@212.81.36.236:9700",
    #     "http://1RzeHb:6AvjQx@212.81.37.8:9669",
    #     "http://1RzeHb:6AvjQx@212.81.37.44:9978",
    #     "http://1RzeHb:6AvjQx@212.81.38.201:9386",
    #     "http://1RzeHb:6AvjQx@212.81.39.75:9002",
    #     "http://1RzeHb:6AvjQx@212.81.36.253:9761",
    #     "http://1RzeHb:6AvjQx@212.81.37.98:9554",
    #     "http://1RzeHb:6AvjQx@212.81.39.175:9712",
    #     "http://1RzeHb:6AvjQx@212.81.38.181:9854",
    #     "http://1RzeHb:6AvjQx@212.81.36.155:9953",
    #     "http://1RzeHb:6AvjQx@212.81.37.91:9437",
    #     "http://1RzeHb:6AvjQx@212.81.36.186:9460",

    # ]
