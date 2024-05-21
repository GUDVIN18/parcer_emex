import pandas as pd
import requests
import threading
from bs4 import BeautifulSoup
import os
from flask import Flask, request, redirect, url_for, flash, send_from_directory, session, render_template
from werkzeug.utils import secure_filename
import ctypes
import random
import datetime
import itertools 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Путь к папке для загрузки файлов
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}  # Разрешенные расширения файлов
app.secret_key = 'very_secret_key_here'
stop_threads = threading.Event()

process_thread = None

@app.route('/')
def index():
    return render_template('index.html', running=process_thread is not None and process_thread.is_alive())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        session['file_path'] = file_path
        flash('File successfully uploaded')
        return redirect(url_for('index'))
    else:
        flash('Allowed file types are .xlsx, .xls')
        return redirect(request.url)



@app.route('/start', methods=['POST'])
def start_process():
    global process_thread
    if 'file_path' not in session:
        flash('No file has been uploaded.')
        return redirect(url_for('index'))
    file_path = session['file_path']
    proxies = load_proxies()
    if process_thread is None or not process_thread.is_alive():
        process_thread = threading.Thread(target=run_process, args=(file_path, proxies))
        process_thread.start()
        flash('Process started')
    else:
        flash('Process is already running')
    return redirect(url_for('index'))



@app.route('/download_results')
def download_results():
    directory = 'results'
    filename = 'final_results.xlsx'
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/stop', methods=['POST'])
def stop_process():
    global threads
    for thread in threads:
        if thread.is_alive():
            terminate_thread(thread)
    flash('All threads have been terminated')
    return redirect(url_for('index'))


#Прерывание ВСЕХ потоков по команде /stop
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


#Загружаем наши прокси  
def load_proxies():
    df = pd.read_excel('proxy/proxy.xlsx')
    proxies_list = df.iloc[:, 0].tolist()
    return proxies_list
# Таким образом, load_proxies() извлекает список прокси-серверов 
# из первого столбца файла Excel и предоставляет его в виде списка 
# Python для дальнейшего использования в программе.





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
        final_df.to_excel(os.path.join('results', final_filename), index=False)
        print(f"All data has been merged into {final_filename}")
    else:
        print("No data to merge.")

def run_process(file_path, proxies):
    df = pd.read_excel(file_path)
    #Разделяем таблицу и прокси на 16 частей (для 16 потоков)
    data_chunks = split_dataframe(df, 16)
    proxy_chunks = split_proxies(proxies, 16)
    
    global threads
    #Потоки
    threads = []
    #Временные файлы
    temp_files = []
    
    for data_chunk, proxy_chunk in zip(data_chunks, proxy_chunks):
        filename = f"results/price_updated_{str(random.randint(0, 9999999))}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        temp_files.append(filename)
        #Запускаем потоки и передаем таблицу, прокси и временный файл filename
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


    
if __name__ == '__main__':
    app.run(debug=True)
