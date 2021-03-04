import os
import hashlib
import concurrent.futures
import shutil
import sys


EXTENSIONS_NOT_TO_HARDLINK = ["-shm"]


def hashfile(filename: str) -> str:
    md5 = hashlib.md5()
    with open(filename, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            md5.update(chunk)
            chunk = file.read(8192)
    return md5.hexdigest()


def create_hard_link(original, link):
    link_folder, link_filename = os.path.split(link)
    link_path = os.path.relpath(original, link_folder)
    os.chdir(link_folder)
    os.system(f'cmd /c mklink /H "{link_filename}" "{link_path}"')


def copy_file(source, destdir, destfile, fsize, hash=None, desthash=None):
    if os.path.isfile(destfile):
        if os.path.getsize(destfile) == fsize:
            if hash is not None:
                if desthash == hash:
                    print(
                        f"Skipping, {destfile} exist and has same hash as original...")
                    return
                else:
                    print(f"Deleting {destfile}. Hash mismatch...")
                    os.remove(destfile)
            else:
                print(f"Skipping, {destfile} exists..")
                # shutil.copystat(source, destfile)
                return
    print(f"Copying {source} to {destdir} ...")
    shutil.copy(source, destdir)
    shutil.copystat(source, destfile)


def shoud_try_hardlink(filename, fsize) -> bool:
    if fsize == 0:
        return False  # do not hardlink zero size file
    for ext in EXTENSIONS_NOT_TO_HARDLINK:
        if filename.lower().endswith(ext):
            return False
    return True


def hash_source_and_dest_file(source, dest, fsize, pool):
    if os.path.exists(dest):
        if os.path.getsize(dest) == fsize:
            return list(pool.map(hashfile, [source, dest]))
    return [hashfile(source), None]


def copy_tree(source_folder, dest_root):
    hash_dict = dict()
    saved = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for current_folder, _, file_list in os.walk(source_folder):
            rel_folder = os.path.relpath(current_folder, source_folder)
            dest_folder = os.path.join(dest_root, rel_folder)
            os.makedirs(dest_folder, exist_ok=True)
            for fname in file_list:
                source_filename = os.path.join(
                    source_folder, rel_folder, fname)
                dest_file = os.path.join(dest_folder, fname)
                fsize = os.path.getsize(source_filename)
                [hash, desthash] = hash_source_and_dest_file(
                    source_filename, dest_file, fsize, pool)
                if shoud_try_hardlink(source_filename, fsize):
                    key = (hash, fsize)
                    if key not in hash_dict:
                        hash_dict[key] = [dest_file, 1]
                        copy_file(source_filename, dest_folder,
                                  dest_file, fsize, hash, desthash)
                    else:
                        [link_source, link_count] = hash_dict[key]
                        if link_count > 1000:
                            copy_file(source_filename, dest_folder,
                                      dest_file, fsize)
                            hash_dict[key] = [dest_file, 1]
                        else:
                            if os.path.isfile(dest_file):
                                print(
                                    f"Do not create hardlink, {dest_file} exists")
                            else:
                                print(f"Creating hardlink for "
                                      f"{dest_file} with {link_source} ...")
                                create_hard_link(link_source, dest_file)
                            hash_dict[key][1] += 1
                            saved += fsize
                else:
                    copy_file(source_filename, dest_folder,
                              dest_file, fsize, hash, desthash)
        print(f"Saved {saved} bytes with hardlinks")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"São necessários 2 argumentos,"
              f" mas foram informados {len(sys.argv)-1}")
        print("Informe a pasta de origem e a de destino da cópia.")
        exit(1)
    source = sys.argv[1]
    dest = sys.argv[2]
    if dest.endswith(":"):
        dest += "\\"
    if not os.path.isdir(source):
        print(f"{source} não é um diretório")
        exit(1)
    if not os.path.isdir(dest):
        print(f"{dest} não é um diretório")
        exit(1)
    copy_tree(source, dest)
    exit(0)
