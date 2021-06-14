import os
import concurrent.futures
import subprocess
import sys


WORKERS = 32

devnull = open(os.devnull, 'w')


def is_wav_file(file_to_test: str) -> bool:
    output = subprocess.run(
        ['ffprobe.exe', file_to_test], capture_output=True).stderr
    if b'pcm_s16le' in output:
        return True
    return False


def convert_wav_to_mp3(wav_file: str) -> bool:
    if not is_wav_file(wav_file):
        print(f"Arquivo     {wav_file} não é um arquivo wav")
        return False

    print(f"Convertendo {wav_file} ...")
    renamed_wav = wav_file + '_oldwav'
    os.rename(wav_file, renamed_wav)
    subprocess.call(['ffmpeg.exe', '-i', renamed_wav, '-codec:a',
                     'libmp3lame', '-qscale:a', '6', wav_file], stderr=devnull,
                    stdout=devnull)
    os.unlink(renamed_wav)
    print(f"Convertido  {wav_file}")
    return True


def collect_files_to_convert(source_folder):
    files_to_convert = []
    for current_folder, _, file_list in os.walk(source_folder):
        for fname in file_list:
            if fname.endswith('_Converted.wav'):
                full_file = os.path.join(current_folder, fname)
                files_to_convert.append(full_file)
    return files_to_convert


def process_dir(dir):
    files_to_convert = collect_files_to_convert(dir)
    if len(files_to_convert) == 0:
        print("Não foram enconrados arquivos para converter")
        exit(0)
    print(f"Convertendo {len(files_to_convert)} arquivos...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        count = sum(pool.map(convert_wav_to_mp3, files_to_convert))
    print(f"Convertidos {count} arquivos de {len(files_to_convert)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"É necessário um argumento (pasta do relatório)."
              f" Foram fornecidos {len(sys.argv)-1}.")
        exit(1)
    dir = sys.argv[1]
    if not os.path.isdir(dir):
        print(f"{dir} não é um diretório")
        exit(1)
    process_dir(dir)
