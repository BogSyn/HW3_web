import os
import shutil
import queue
import logging
import time
import threading


# Словник розширень
extensions_dir = {
    'Music': ('.mp3', '.aac', '.wma', '.flac', '.midi', '.amr',),
    'Video': ('.mp4', '.wav', '.avi', '.mkv', '.mpeg',),
    'Image': ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.svg',),
    'Text': ('.txt', '.rtf', '.doc', '.docx', '.xls', '.xlsx', '.ppt',
             '.pptx', '.pdf', '.odt', '.ods', '.odp', '.odg', '.odf',
             '.odg', '.ods', '.odp', '.odg', '.odf', '.odg', '.ods',
             '.odp', '.odg', '.odf', '.odg', '.ods', '.odp',),
    'Archives': ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',),
}

# Створюємо чергу для передачі файлів потокам.
folder_queue = queue.Queue()

# Створюємо чергу для передачі файлів потокам.
file_queue = queue.Queue()

# Створюємо список потоків
threads = []

def mk_archive(directory):
    """Створюємо архів з теки directory.

    Args:
        directory (str): шлях до теки, що архівується.

    Returns:
        None
    """
    name_archive = os.path.basename(directory)
    shutil.make_archive(base_name=name_archive, format="zip", root_dir=directory)


def folder_searcher(directory):
    """
        Пошук і додавання до черги всіх тек за вказаним шляхом.

        Parameters:
            directory (str): директорія в якій ведеться пошук тек.

        Returns:
            None
        """
    for folder in os.listdir(directory):
        # logging.debug(f"{os.path.basename(directory)}")
        if os.path.isdir(os.path.join(directory, folder)):
            folder_queue.put(os.path.join(directory, folder))
            #
            th = threading.Thread(target=folder_searcher, args=(os.path.join(directory, folder),))
            th.daemon = True
            threads.append(th)
            th.start()


def file_searcher(directory):
    """
        Пошук і додавання до черги всіх файлів за вказаним шляхом.

        Args:
            directory (str): директорія в якій ведеться пошук файлів.

        Returns:
            None
        """
    # logging.debug(f"{os.path.basename(directory)}")
    for folder in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, folder)):
            file_queue.put(os.path.join(directory, folder))


def file_moving(file_path, directory):
    """
        Свореня теки за розширенням файлу та переміщення файлу в створену теку.

        Args:
            file_path (str): Повний шлях файлу звідки перемістити.
            directory (str): Повний шлях файлу куди перемістити.

        Returns:
            None
        """
    # logging.debug(f"{os.path.basename(file_path)}")
    dir_path = os.path.dirname(directory)
    extension = os.path.splitext(os.path.basename(file_path))[1]
    folder = []

    for key, value in extensions_dir.items():
        if extension in value:
            folder.append(os.path.join(dir_path, key))

    if not folder:
        folder.append(os.path.join(dir_path, "Other"))

    try:
        os.mkdir(folder[0])
    except FileExistsError:
        # logging.warning(f"folder {os.path.basename(folder[0])} already exists")
        pass

    try:
        shutil.move(file_path, folder[0])
    except Exception:
        # logging.warning(f"file {os.path.basename(file_path)} already exists")
        pass

    folder.clear()


def handler(directory):
    file_searcher(directory)
    folder_searcher(directory)
    while True:

        # Отримуємо папку з черги.
        path_folder = folder_queue.get()

        # Робимо потоки
        th = threading.Thread(target=file_searcher, args=(path_folder,))
        th.daemon = True
        th.start()
        threads.append(th)

        # Якщо черга порожня, то виходимо з циклу.
        if folder_queue.empty():
            break

    while True:

        # Отримуємо файл з черги.
        path_file = file_queue.get()

        # Робимо потоки
        th = threading.Thread(target=file_moving, args=(path_file, directory,))
        th.daemon = True
        th.start()
        threads.append(th)

        # Якщо черга порожня, то виходимо з циклу.
        if file_queue.empty():
            break

    [el.join() for el in threads]


if __name__ == "__main__":
    start_time = time.time()
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    garbage = "C:\\Users\\Bohdan\\Desktop\\Folder\\junk"
    # mk_archive(garbage)
    handler(garbage)

    print("Видалляється початкова теку...")

    time.sleep(3)

    try:
        shutil.rmtree(garbage)
        print(f'Теку {os.path.basename(garbage)} та її вміст успішно видалено')
    except OSError as e:
        print(f'Помилка видалення теки: {e}')

    end_time = time.time()
    print(end_time - start_time)
