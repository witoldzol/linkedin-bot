with open('quotes', 'r') as f:
    c = chr(8211)
    for l in f:
        msg, author = l.rsplit(c,1)
        author = author.strip()
        msg = msg.strip()
        print(f'{msg}\n- {author}')
