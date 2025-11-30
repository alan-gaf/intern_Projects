import hashlib
import itertools
import string
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import argparse

hash_name = ['md5','sha1','sha224','sha256','sha384','sha3_224','sha3_256','sha3_384','sha3_512','sha512']

def count_lines(file):
    c = 0
    with open(file,'r')as f:
        for _ in f:
            c+=1
        return c

def generate_passwords(min,max,chars):
    for len in range(min,max+1):
        for pwd in itertools.product(chars,repeat=len):
            yield ''.join(pwd)

def wlist(wordlist):
    with open(wordlist,'r') as f:
        for line in f:
            yield line.strip()

def check_hash(hash_fn,password,target_hash):
    return hash_fn(password.encode()).hexdigest() == target_hash



def crack_hash(hash,wordlist=None,hash_type = 'md5',min =0 ,max = 0 ,chars = string.ascii_letters+string.digits,max_workers = 4):
    hash_fn = getattr(hashlib,hash_type,None)
    if hash_fn is None or hash_type not in hash_name:
        raise ValueError(f'[!]Invalid Hash Type : {hash_type} supported are {hash_name}')
    if wordlist:
        list = wlist(wordlist)
        total_lines = sum(1 for _ in wordlist)

        with ThreadPoolExecutor(max_workers = max_workers)as exe:
            futures = {exe.submit(check_hash,hash_fn,line,hash):line for line in list}
            for future in tqdm(futures,total=total_lines,desc='Cracking Hash'):
                if future.result():
                    for remaining in futures:
                        remaining.cancel()
                    return futures[future].strip()
    elif min>0 and max>0:
        total_combinations = sum(len(chars)** length for length in range(min,max+1))
        print(f"[+]cracking hash {hash} using {hash_type}")
        with ThreadPoolExecutor(max_workers=max_workers) as exe :
            futures=[]
            with tqdm(total = total_combinations,desc = "generating and cracking hash")as pbar:
                for pwd in generate_passwords(min,max,chars):
                    future = exe.submit(check_hash,hash_fn,pwd,hash)
                    futures.append(future)
                    pbar.update(1)
                    if future.result():
                        for remaining in futures:
                            remaining.cancel()
                        return pwd
    return None
            


if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Hash cracker")
    parser.add_argument('hash',help='hash to crack')
    parser.add_argument('-w','--wordlist',help='wordlist of passwords')
    parser.add_argument('--hash_type',help='hash algorithm used',default ='md5')
    parser.add_argument('--min',type= int,help='Minimum length of generation')
    parser.add_argument('--max',type=int,help='maximum length of generation')
    parser.add_argument('-c',help='characters')
    parser.add_argument('--max_workers',help='Multithreading')

    args = parser.parse_args()
    cracked_passwords = crack_hash(args.hash,args.wordlist,args.hash_type,args.min,args.max,args.c,args.max_workers)
    if cracked_passwords:
        print(f'[+]found Password : {cracked_passwords}')
    else:
        print(f'Password not found')