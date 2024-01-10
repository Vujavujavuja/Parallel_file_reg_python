# Paralelni Algoritmi, prvi projekat,2023

## Studenti
Nemanja Vujic 63/21RN

## Urađeno
Registar fajlova: fileregistry.py, file_registry u main.py
  Jedinstveni File ID preko uuid4
  Status fajla (ready i not ready)
  Naziv fajla
  Delovi tog fajla
  
Registar delova: partregistry.py, part_registry u main.py
  Jedinstveni Part ID
  md5hash
  Status dela (ready i not ready)
  
Nit za prihvatanje komandi
  put <file name>
  get <file_id>
  delete <file_id>
  list
  exit
  help

Nit za obradu komandi
  Kad god se pozove neka komanda stvara se novi thread primer:
    thread = threading.Thread(target=get, args=(file_id,))
              thread.start()
              threads.append(thread)

Procesi I/O
  Uz multiprocessing.Pool

Komande
  put
    Prosledjuje se jeinstveni id
    Cita fajl deo po deo i dodlejuje part ID
    Dodaje delove u part_registry
    Delove prosledjuje u grupi na I/O proces
    Racuna md5
    Fajl sa istim imenom moze da se doda vise puta sa drugacijim IDom 
  get
    Pronalazi fajl u file_registry uz file_id
    Uzima listu delova
    Salje listu u I/O
  delete
    Pronalazi fajl i promeni status na not ready
    Pronalazi delove vezane za taj fajl i njih isto oznaci sa not ready
    Salje na I/O sa zahtevom za vrisanje
    Brise delove iz registra delova
    Brise delove iz storage_dir
    Brise fajl iz registra fajlova
  list
    Ispisjue listu file_id-ova imena i statusa fajlova iz file_registry-a
  exit
    Gasi niti
    izlazi 
    
Sistem bi trebalo  da moze da procesira vise komandi, i vodi racuna o zauzetoj memoriji uz MAX_MEMORY_LIMIT i current_memory_usage
Sistem vodi evidenciju koliko delova fajlova je u memoriji
(MAX_MEMORY nije u config.yaml vec na vrhu main.py)

## AI
Povezivanje Visual Studio Code-a sa GitHub-om

Traceback (most recent call last):
  File "C:\Users\necav\PycharmProjects\paralelni-algoritmi-prvi-projekat-tim_nemanjavujic\loader.py", line 9, in <module>
    config = load_config()
             ^^^^^^^^^^^^^
  File "C:\Users\necav\PycharmProjects\paralelni-algoritmi-prvi-projekat-tim_nemanjavujic\loader.py", line 5, in load_config
    config = yaml.load(f)
             ^^^^^^^^^^^^
TypeError: load() missing 1 required positional argument: 'Loader

Exception in thread Thread-5 (delete):
Traceback (most recent call last):
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.1776.0_x64__qbz5n2kfra8p0\Lib\threading.py", line 1045, in _bootstrap_inner
    self.run()
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.1776.0_x64__qbz5n2kfra8p0\Lib\threading.py", line 982, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\necav\PycharmProjects\paralelni-algoritmi-prvi-projekat-tim_nemanjavujic\app\main.py", line 132, in delete
    prats_from_file = file_registry.files[file_id]['parts']
                      ~~~~~~~~~~~~~~~~~~~^^^^^^^^^
KeyError: '1'

Unresolved attribute reference 'notify_all' for class 'Lock' 
Unresolved attribute reference 'wait' for class 'Lock'
