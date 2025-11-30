import itertools
import pikepdf
from tqdm import tqdm
import string
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
import os

def generate_passwords(chars,min,max):
    for len in range(min,max+1):
        for password in itertools.product(chars,repeat=len):
            yield ''.join(password)

def load_wordlist(wordlist):
    with open(wordlist,"r",encoding="utf-8",errors="ignore") as file:
        for line in file:
            yield line.strip()

def try_password(file,password):
    try:
        with pikepdf.open(file,password=password) as pdf:
            print('[+]Password Found: ',{password})
            return password
    except pikepdf._core.PasswordError:
        return None
    


def decrypt_pdf_fast(pdf_path, passwords_iterable, total_passwords=None,max_workers=None, prefetch_factor=2):

    cpu_count = os.cpu_count() or 1
    if max_workers is None:
        max_workers = max(1, cpu_count - 1)

    prefetch = max_workers * max(1, prefetch_factor)

    pw_iter = iter(passwords_iterable)

    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        futures = {}
        try:
            for _ in range(prefetch):
                pwd = next(pw_iter)
                fut = exe.submit(try_password,pdf_path, pwd)
                futures[fut] = pwd
        except StopIteration:
            pass
        with tqdm(total=total_passwords, desc="Decrypting PDF", unit="pwd") as pbar:
            while futures:
                for fut in as_completed(futures):
                    pwd = futures.pop(fut)
                    result = fut.result()
                    pbar.update(1)
                    if result:
                        for remaining in futures:
                            remaining.cancel()
                        return result
                    try:
                        next_pwd = next(pw_iter)
                        new_fut = exe.submit(try_password,pdf_path,next_pwd)
                        futures[new_fut] = next_pwd
                    except StopIteration:
                        pass
                    break
    return None


def main():
    parser = argparse.ArgumentParser(description="Decrypt pdf.")
    parser.add_argument('pdf_file',help='Path to Pdf')
    parser.add_argument('-w','--wordlist',help='Path to wordlist',default=None)
    parser.add_argument('-g','--generate',action='store_true',help='generate passwords')
    parser.add_argument('-min','--min_length',type=int,help='minimum length of password',default=1)
    parser.add_argument('-max','--max_length',type=int,help='maximum length of password',default=3)
    parser.add_argument('-c','--charset',type=str,help='Character set for password generation',default=string.ascii_letters)
    parser.add_argument('--max_workers',type=int,help='workers for multithreading',default = 4)

    args = parser.parse_args()
    if args.generate:
        passwords = generate_passwords(args.charset,args.min_length,args.max_length)
        total_passwords= sum(1 for _ in generate_passwords(args.charset,args.min_length,args.max_length))
    elif args.wordlist:
        passwords = load_wordlist(args.wordlist)
        total_passwords = sum(1 for _ in load_wordlist(args.wordlist))
    else:
        print('Provide --wordlist or specify --generate')
        exit(1)

    decrypt_password = decrypt_pdf_fast(pdf_path=args.pdf_file,passwords_iterable=passwords,total_passwords=total_passwords)
    if decrypt_password:
        print(f'PDF decrypted successfully\nPassword: ',{decrypt_password})
    else:
        print('Unable to Decrypt PDF')



if __name__ == '__main__':
    main()
                    