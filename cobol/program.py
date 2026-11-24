#!/usr/bin/env python3
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS = os.path.join(BASE, "data", "ACCOUNTS.DAT")
BOOKS = os.path.join(BASE, "data", "BOOKS.DAT")
TRANSACTIONS = os.path.join(BASE, "data", "TRANSACTIONS.DAT")
INPUT_FILE = os.path.join(BASE, "src", "INPUT.DAT")

ACCT_REC = 34  # 4 + 20 + 10
BOOK_REC = 28  # 4 + 20 + 4
TRAN_REC = 22  # 4 + 10 + 4 + 4
INPUT_REC = 22  # 4 + 4 + 4 + 10


def read_input():
    with open(INPUT_FILE, "rb") as f:
        data = f.read()
    if len(data) < INPUT_REC:
        data = data + b" " * (INPUT_REC - len(data))
    buyer = data[0:4]
    seller = data[4:8]
    book = data[8:12]
    amount_bytes = data[12:22]
    s = amount_bytes.decode("latin-1").strip().strip("\x00")
    amount = int(s) if s else 0
    return buyer, seller, book, amount


def split_records(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]


def main():
    try:
        with open(INPUT_FILE, "rb") as f:
            _ = f.read()
    except FileNotFoundError:
        print("Error: Input file is empty")
        return
    if os.path.getsize(INPUT_FILE) == 0:
        print("Error: Input file is empty")
        return

    buyer, seller, book, amount = read_input()

    with open(ACCOUNTS, "rb") as f:
        accounts = split_records(f.read(), ACCT_REC)
    with open(BOOKS, "rb") as f:
        books = split_records(f.read(), BOOK_REC)

    buyer_found = any(r[0:4] == buyer for r in accounts)
    seller_found = any(r[0:4] == seller for r in accounts)
    book_found = False
    valid_owner = False
    for r in books:
        if r[0:4] == book:
            book_found = True
            if r[24:28] == seller:
                valid_owner = True

    print(" ")

    if not (buyer_found and seller_found and book_found and valid_owner):
        print("Transaction failed due to validation errors")
        return

    new_accounts = []
    for r in accounts:
        aid = r[0:4]
        name = r[4:24]
        bal = int(r[24:34].decode("latin-1"))
        if aid == buyer:
            bal -= amount
        if aid == seller:
            bal += amount
        bal_str = f"{bal:010d}".encode("latin-1")
        new_accounts.append(aid + name + bal_str)
    with open(ACCOUNTS, "wb") as f:
        f.write(b"".join(new_accounts))

    new_books = []
    for r in books:
        bid = r[0:4]
        title = r[4:24]
        owner = r[24:28]
        if bid == book:
            owner = buyer
        new_books.append(bid + title + owner)
    with open(BOOKS, "wb") as f:
        f.write(b"".join(new_books))

    amount_str = f"{amount:010d}".encode("latin-1")
    trans_record = book + amount_str + seller + buyer
    with open(TRANSACTIONS, "ab") as f:
        f.write(trans_record)

    print("Transaction completed successfully")


if __name__ == "__main__":
    main()
