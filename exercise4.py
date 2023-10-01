# 导入所需库
import nltk
import sqlite3
import gensim
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
from nltk.corpus import gutenberg

nltk.download('gutenberg')

# 加载《爱丽丝梦游仙境》文本
alice_corpus = gutenberg.sents('carroll-alice.txt')

# 打印前5个句子
for sentence in alice_corpus[:5]:
    print(' '.join(sentence))

# 连接数据库
conn = sqlite3.connect('library.db')
cursor = conn.cursor()



# 创建表格
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID INTEGER PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        ISBN TEXT,
        Status TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY,
        Name TEXT,
        Email TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReservationID INTEGER PRIMARY KEY,
        BookID INTEGER,
        UserID INTEGER,
        ReservationDate DATE,
        FOREIGN KEY (BookID) REFERENCES Books (BookID),
        FOREIGN KEY (UserID) REFERENCES Users (UserID)
    )
''')
conn.commit()

# 添加新书到数据库的函数
def add_book():
    title = input("请输入书名: ")
    author = input("请输入作者: ")
    isbn = input("请输入ISBN: ")
    status = input("请输入书籍状态: ")
    
    cursor.execute('''
        INSERT INTO Books (Title, Author, ISBN, Status)
        VALUES (?, ?, ?, ?)
    ''', (title, author, isbn, status))
    conn.commit()
    print("书籍添加成功。")

# 根据书籍ID查找书籍详情的函数
def find_book_details(book_id):
    cursor.execute('''
        SELECT Books.*, Users.Name, Reservations.ReservationDate
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
        WHERE Books.BookID = ?
    ''', (book_id,))

result = cursor.fetchone()

if result:
    book_id, title, author, isbn, status, user_name, reservation_date = result
    if user_name:
        print(f"书籍ID：{book_id}")
        print(f"书名：{title}")
        print(f"作者：{author}")
        print(f"ISBN：{isbn}")
        print(f"状态：{status}")
        print(f"借阅者：{user_name}")
        print(f"借阅日期：{reservation_date}")
    else:
        print(f"书籍ID：{book_id}")
        print(f"书名：{title}")
        print(f"作者：{author}")
        print(f"ISBN：{isbn}")
        print(f"状态：{status}")
        print("该书未被任何人借阅。")
else:
    print("未找到书籍。")

# 根据输入的文本查找书籍的借阅状态
def find_reservation_status(search_text):
    if search_text.startswith("LB"):
        column = "Books.BookID"
    elif search_text.startswith("LU"):
        column = "Users.UserID"
    elif search_text.startswith("LR"):
        column = "Reservations.ReservationID"
    else:
        # 输入的文本不符合任何列的起始标识，表示书籍不存在
        print("书籍不存在。")
        return

    cursor.execute('''
        SELECT Books.*, Users.Name, Reservations.ReservationDate
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
        WHERE {} = ?
    '''.format(column), (search_text,))
    result = cursor.fetchone()

    if result:
        book_id, title, author, isbn, status, user_name, reservation_date = result
        if user_name:
            print(f"书籍ID：{book_id}")
            print(f"书名：{title}")
            print(f"作者：{author}")
            print(f"ISBN：{isbn}")
            print(f"状态：{status}")
            print(f"借阅者：{user_name}")
            print(f"借阅日期：{reservation_date}")
        else:
            print(f"书籍ID：{book_id}")
            print(f"书名：{title}")
            print(f"作者：{author}")
            print(f"ISBN：{isbn}")
            print(f"状态：{status}")
            print("该书未被任何人借阅。")
    else:
        print("书籍不存在。")

# 查询数据库中所有书籍的函数
def find_all_books():
    cursor.execute('''
        SELECT Books.*, Users.Name, Reservations.ReservationDate
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
    ''')
    results = cursor.fetchall()

    for result in results:
        book_id, title, author, isbn, status, user_name, reservation_date = result
        if user_name:
            print(f"书籍ID：{book_id}")
            print(f"书名：{title}")
            print(f"作者：{author}")
            print(f"ISBN：{isbn}")
            print(f"状态：{status}")
            print(f"借阅者：{user_name}")
            print(f"借阅日期：{reservation_date}")
        else:
            print(f"书籍ID：{book_id}")
            print(f"书名：{title}")
            print(f"作者：{author}")
            print(f"ISBN：{isbn}")
            print(f"状态：{status}")
            print("该书未被任何人借阅。")

# 修改书籍详情的函数
def update_book_details(book_id):
    new_status = input("请输入新的书籍状态: ")
    new_author = input("请输入新的作者名字: ")
    
    cursor.execute('''
        UPDATE Books
        SET Status = ?, Author = ?
        WHERE BookID = ?
    ''', (new_status, new_author, book_id))
    conn.commit()
    print("书籍详情已更新。")

# 删除书籍的函数
def delete_book(book_id):
    cursor.execute('''
        DELETE FROM Books
        WHERE BookID = ?
    ''', (book_id,))
    cursor.execute('''
        DELETE FROM Reservations
        WHERE BookID = ?
    ''', (book_id,))
    conn.commit()
    print("书籍已删除。")

    # 加载Alice's Adventures in Wonderland文本
    corpus = nltk.corpus.gutenberg.sents('carroll-alice.txt')

    # 进行数据预处理
    processed_corpus = [[word.lower() for word in sent if word.isalpha()] for sent in corpus]

    # 构建词频词典
    dictionary = gensim.corpora.Dictionary(processed_corpus)

    # 构建文档词袋模型
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_corpus]

    # 执行LDA主题建模
    lda_model = gensim.models.LdaModel(bow_corpus, num_topics=5, id2word=dictionary)

    # 可视化主题模型
    vis_data = gensimvis.prepare(lda_model, bow_corpus, dictionary)
    pyLDAvis.display(vis_data)

# 主程序
while True:
    print("请选择操作：")
    print("1. 添加新书")
    print("2. 查找书籍详情")
    print("3. 查找书籍借阅状态")
    print("4. 查找所有书籍")
    print("5. 修改书籍详情")
    print("6. 删除书籍")
    print("7. 退出")
    
    choice = input("请输入数字选择操作: ")
    
    if choice == "1":
        add_book()
    elif choice == "2":
        book_id = input("请输入书籍ID: ")
        find_book_details(book_id)
    elif choice == "3":
        search_text = input("请输入搜索内容: ")
        find_reservation_status(search_text)
    elif choice == "4":
        find_all_books()
    elif choice == "5":
        book_id = input("请输入书籍ID: ")
        update_book_details(book_id)
    elif choice == "6":
        book_id = input("请输入书籍ID: ")
        delete_book(book_id)
    elif choice == "7":
        break
    else:
        print("无效的选择，请重新输入。")


