import pandas as pd
import os
import re

def merge_excel_files(directory, output_file):
    # Создаем пустой список для хранения данных из всех файлов
    all_data = []

    # Проходим по всем файлам в указанной директории
    for file in os.listdir(directory):
        # Проверяем, соответствует ли имя файла шаблону 'price_updated_(число)_(дата).xlsx'
        if re.match(r'price_updated_\d+_\d+\.xlsx$', file):
            # Формируем полный путь к файлу
            file_path = os.path.join(directory, file)
            # Читаем файл Excel и добавляем его содержимое в список
            df = pd.read_excel(file_path)
            all_data.append(df)

    # Объединяем все DataFrame из списка в один
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        # Сохраняем объединенный DataFrame в новый файл Excel
        combined_df.to_excel(os.path.join(directory, output_file), index=False)
        print(f"Все данные были объединены и сохранены в файл: {output_file}")
    else:
        print("Файлы, соответствующие шаблону, не найдены.")

# Пример использования функции
merge_excel_files('results', 'final_combined_file.xlsx')
