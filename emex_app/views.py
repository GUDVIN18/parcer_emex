import os
import threading
import random
import datetime
import itertools
import ctypes
import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
stop_threads = threading.Event()
process_thread = None
threads = []


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Перенаправление на главную страницу после успешного входа
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль!')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def index(request):
    return render(request, 'index.html', {'running': process_thread is not None and process_thread.is_alive()})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        if allowed_file(file.name):
            fs = FileSystemStorage(location=UPLOAD_FOLDER)
            filename = fs.save(file.name, file)
            request.session['file_path'] = os.path.join(UPLOAD_FOLDER, filename)
            messages.success(request, 'Файл успешно загружен')
            return redirect('index')
        else:
            messages.error(request, 'Файл должен иметь формат .xlsx, .xls')
            return redirect('index')
    return redirect('index')

def start_process(request):
    global process_thread
    if 'file_path' not in request.session:
        messages.error(request, 'Ни один файл не был загружен.')
        return redirect('index')
    file_path = request.session['file_path']
    proxies = load_proxies()
    if process_thread is None or not process_thread.is_alive():
        process_thread = threading.Thread(target=run_process, args=(file_path, proxies))
        process_thread.start()
        messages.success(request, 'Процесс запущен!')
    else:
        messages.warning(request, 'Процесс уже запущен')
    return redirect('index')

def download_results(request):
    file_path = os.path.join('emex_app/results', 'final_results.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    messages.error(request, 'Файл не найден')
    return redirect('index')

def stop_process(request):
    global threads
    for thread in threads:
        if thread.is_alive():
            terminate_thread(thread)
    messages.success(request, 'Все потоки были прерваны\nНе закрывайте программу!\nВы можете скачать содержимое через 15мин после остановки!')
    return redirect('index')

def terminate_thread(thread):
    """Принудительное завершение потока"""
    if not thread.is_alive():
        return
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def load_proxies():
    df = pd.read_excel('emex_app/proxy/proxy.xlsx')
    proxies_list = df.iloc[:, 0].tolist()
    return proxies_list

def split_dataframe(df, num_parts):
    chunk_size = len(df) // num_parts
    return [df.iloc[i * chunk_size:(i + 1) * chunk_size] for i in range(num_parts)]

def split_proxies(proxies, num_parts):
    chunk_size = len(proxies) // num_parts
    return [proxies[i * chunk_size:(i + 1) * chunk_size] for i in range(num_parts)]

def save_temp_results(data_chunk, filename):
    """Сохраняем результаты потока во временный файл"""
    temp_filename = f"temp_{filename}"
    data_chunk.to_excel(temp_filename, index=False)
    return temp_filename

def merge_results(temp_files, final_filename):
    """Считываем все временные файлы и объединяем их в один финальный файл"""
    all_data = []
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            df = pd.read_excel(temp_file)
            all_data.append(df)
            os.remove(temp_file)  # Удаляем временный файл после его считывания
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_excel(os.path.join('emex_app/results', final_filename), index=False)
        print(f"All data has been merged into {final_filename}")
    else:
        print("No data to merge.")

def run_process(file_path, proxies):
    df = pd.read_excel(file_path)
    data_chunks = split_dataframe(df, 16)
    proxy_chunks = split_proxies(proxies, 16)

    global threads
    threads = []
    temp_files = []

    for data_chunk, proxy_chunk in zip(data_chunks, proxy_chunks):
        filename = f"emex_app/results/price_updated_{str(random.randint(0, 9999999))}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        temp_files.append(filename)
        thread = threading.Thread(target=process_data, args=(data_chunk, proxy_chunk, filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    merge_results(temp_files, 'final_results.xlsx')
    print('All threads have completed or have been terminated.')

def process_data(data_chunk, proxy_chunk, filename):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Android 10; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0",
        "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
        "Mozilla/5.0 (Android 8.0.0; Mobile; rv:68.0) Gecko/68.0 Firefox/68.0",
        "Mozilla/5.0 (iPad; CPU OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D100 Safari/604.1",
        "Mozilla/5.0 (Android 9; Tablet; rv:68.0) Gecko/68.0 Firefox/68.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
    ]
    cycle_proxies = itertools.cycle(proxy_chunk)
    cycle_user_agents = itertools.cycle(user_agents)
    while not stop_threads.is_set():
        try:
            for index, row in data_chunk.iterrows():
                articl = str(row['Артикул'])
                marka = str(row['Брэнд']).replace(' / ', '%20%2F%20')
                price = row['Цена']

                url = f'https://emex.ru/products/{articl}/{marka}/38760'

                proxy = next(cycle_proxies)
                user_agent = next(cycle_user_agents)
                headers = {'User-Agent': user_agent}
                proxy_dict = {'http': proxy, 'https': proxy}

                attempts = 0
                while attempts < 5:
                    try:
                        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=5)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                        num = soup.find('td', class_='sc-6610f28-11 sc-6610f28-13 gRBmRM bfctEY').text if soup.find('td', class_='sc-6610f28-11 sc-6610f28-13 gRBmRM bfctEY') else 'Не опознано'
                        ip = soup.find('div', {'data-testid': 'Offers:text:priceInfo'})

                        if ip:
                            price_text = ip.find('span').text.strip().replace(" ", "")
                            new_price = float(price_text) - 1 
                            if new_price < (price + (price * 0.07)):
                                new_price = price + (price * 0.07)
                            data_chunk.at[index, 'Новая цена'] = new_price
                            print(f'Success: {articl} at {new_price}')
                        break

                    except requests.exceptions.RequestException as e:
                        print(f"Request error for {url}: {e}, trying next proxy.")
                        attempts += 1

                if attempts == 5:
                    print(f"Failed all attempts for {articl}")
        except SystemExit:
            # Сохраняем изменения в файл 
            data_chunk.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            break

        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            data_chunk.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            break
    print('все потоки остановлены!')
