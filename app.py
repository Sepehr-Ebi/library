from flask import Flask, render_template, request, redirect, flash
from datetime import datetime
import json


app = Flask(__name__)
app.secret_key = "library-secret-key"


# =====================
# DATABASE FUNCTIONS
# =====================

def load_books():

    with open("books.json", "r", encoding="utf-8") as file:
        return json.load(file)



def save_books(books):

    with open("books.json", "w", encoding="utf-8") as file:
        json.dump(
            books,
            file,
            indent=4,
            ensure_ascii=False
        )



# =====================
# HOME
# =====================

@app.route("/")
def home():

    books = load_books()

    return render_template(
        "index.html",
        books=books
    )



# =====================
# ADD BOOK
# =====================

@app.route("/add", methods=["GET", "POST"])
def add_book():


    if request.method == "POST":


        books = load_books()


        if books:
            new_id = str(max(map(int, books.keys())) + 1)

        else:
            new_id = "101"



        books[new_id] = {

            "title": request.form["title"].title(),

            "author": request.form["author"],

            "year": int(request.form["year"]),

            "genre": request.form["genre"],

            "available": True,

            "borrower": None

        }



        save_books(books)
        flash("✅ کتاب با موفقیت اضافه شد", "success")

        return redirect("/")



    return render_template(
        "add_book.html"
    )



# =====================
# BOOK PAGE
# =====================

@app.route("/book/<book_id>")
def book_page(book_id):


    books = load_books()


    if book_id not in books:
        return redirect("/")



    return render_template(

        "book.html",

        book=books[book_id],

        book_id=book_id

    )



# =====================
# SEARCH
# =====================

@app.route("/search")
def search_books():


    books = load_books()


    query = request.args.get(
        "q",
        ""
    ).lower().strip()



    results = {}



    for book_id, book in books.items():


        if (

            query in book["title"].lower()

            or query == book["author"].lower()

            or query == book["genre"].lower()

        ):

            results[book_id] = book



    return render_template(

        "search.html",

        books=results,

        query=query

    )



# =====================
# BORROW BOOK
# =====================

@app.route("/borrow/<book_id>", methods=["GET", "POST"])
def borrow_book(book_id):

    books = load_books()


    if book_id not in books:
        return redirect("/")



    book = books[book_id]



    if request.method == "POST":


        borrower = request.form["borrower"]



        book["borrower"] = borrower

        book["available"] = False




        # ساخت تاریخچه اگر وجود نداشت

        if "history" not in book:

            book["history"] = []




        # ثبت اتفاق امانت

        book["history"].append({

            "borrower": borrower,

            "action": "borrow",

            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        })





        save_books(books)



        flash(
            "📥 کتاب با موفقیت امانت داده شد",
            "success"
        )



        return redirect(f"/book/{book_id}")





    return render_template(

        "borrow.html",

        book=book,

        book_id=book_id

    )



# =====================
# RETURN BOOK
# =====================

@app.route("/return/<book_id>")
def return_book(book_id):

    books = load_books()


    if book_id not in books:
        return redirect("/")



    book = books[book_id]


    now = datetime.now()



    if "history" not in book:

        book["history"] = []



    borrow_time = None



    # پیدا کردن آخرین امانت

    for item in reversed(book["history"]):

        if item["action"] == "borrow":

            borrow_time = datetime.strptime(

                item["date"],

                "%Y-%m-%d %H:%M:%S"

            )

            break





    duration = None



    if borrow_time:


        duration = now - borrow_time



        duration = str(duration).split(".")[0]




    book["history"].append({

        "borrower": book.get("borrower"),

        "action": "return",

        "date": now.strftime("%Y-%m-%d %H:%M:%S"),

        "duration": duration

    })





    book["available"] = True

    book["borrower"] = None



    save_books(books)



    flash(

        "📤 کتاب پس گرفته شد",

        "success"

    )


    return redirect(f"/book/{book_id}")



# =====================
# EDIT BOOK
# =====================

@app.route("/edit/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):


    books = load_books()


    if book_id not in books:
        return redirect("/")



    book = books[book_id]



    if request.method == "POST":


        book["title"] = request.form["title"].title()

        book["author"] = request.form["author"]

        book["year"] = int(request.form["year"])

        book["genre"] = request.form["genre"]



        save_books(books)
        flash("✏️ تغییرات کتاب ذخیره شد", "success")



        return redirect(f"/book/{book_id}")



    return render_template(

        "edit_book.html",

        book=book,

        book_id=book_id

    )



# =====================
# DELETE BOOK
# =====================

@app.route("/delete/<book_id>")
def delete_book(book_id):

    books = load_books()


    if book_id not in books:
        return redirect("/")



    book = books[book_id]



    # جلوگیری از حذف کتاب امانت داده شده

    if not book["available"]:

        flash("⚠️ این کتاب امانت داده شده و قابل حذف نیست", "danger")
        return redirect(f"/book/{book_id}")



    books.pop(book_id)


    save_books(books)
    flash("🗑 کتاب حذف شد", "success")


    return redirect("/")


# =====================
# DASHBOARD
# =====================

@app.route("/dashboard")
def dashboard():

    books = load_books()


    total_books = len(books)

    available_books = 0

    borrowed_books = 0



    # تعداد امانت هر ژانر

    genre_count = {}



    # تعداد امانت هر کتاب

    book_reads = {}



    # اطلاعات کامل هر کتاب

    book_stats = {}



    # تاریخچه کلی

    history = []



    # زمان‌های مطالعه

    total_read_time = []



    # کتاب‌های در حال امانت

    borrow_status = []





    for book_id, book in books.items():



        # مقدار اولیه آمار کتاب

        book_stats[book_id] = {

            "title": book["title"],

            "count": 0,

            "history": book.get("history", [])

        }




        # وضعیت کتاب


        if book.get("available"):

            available_books += 1


        else:

            borrowed_books += 1



            last_borrow = None



            for item in reversed(book.get("history", [])):


                if item.get("action") == "borrow":


                    last_borrow = item.get("date")

                    break




            borrow_status.append({

                "id": book_id,

                "title": book["title"],

                "borrower": book.get("borrower"),

                "date": last_borrow

            })







        # بررسی تاریخچه


        for item in book.get("history", []):



            history.append({

                "id": book_id,

                "title": book["title"],

                "action": item.get("action"),

                "borrower": item.get("borrower"),

                "date": item.get("date"),

                "duration": item.get("duration")

            })






            # آمار امانت


            if item.get("action") == "borrow":



                genre = book["genre"]



                genre_count[genre] = genre_count.get(

                    genre,

                    0

                ) + 1






                book_reads[book["title"]] = book_reads.get(

                    book["title"],

                    0

                ) + 1






                book_stats[book_id]["count"] += 1







            # مدت مطالعه


            if item.get("action") == "return":


                if item.get("duration"):


                    total_read_time.append(

                        item["duration"]

                    )









    # محبوب ترین ژانر


    if genre_count:


        popular_genre = max(

            genre_count,

            key=genre_count.get

        )


    else:


        popular_genre = "ندارد"







    # پرخواننده ترین کتاب


    if book_reads:


        popular_book = max(

            book_reads,

            key=book_reads.get

        )


    else:


        popular_book = "ندارد"








    stats = {


        "total": total_books,


        "available": available_books,


        "borrowed": borrowed_books,



        "popular_genre": popular_genre,


        "popular_book": popular_book,



        "history": history,



        "genre_stats": genre_count,



        "book_stats": book_stats,



        "borrow_status": borrow_status,



        "read_times": total_read_time,



        "books": books


    }






    return render_template(

        "dashboard.html",

        stats=stats

    )



# =====================
# ALL BOOKS PAGE
# =====================

@app.route("/books")
def all_books():

    books = load_books()

    return render_template(
        "books.html",
        books=books
    )





# =====================
# BORROWED BOOKS PAGE
# =====================

@app.route("/borrowed")
def borrowed_books():

    books = load_books()

    borrowed = {}


    for book_id, book in books.items():

        if not book.get("available"):

            borrowed[book_id] = book



    return render_template(
        "borrowed.html",
        books=borrowed
    )




# =====================
# AVAILABLE BOOKS
# =====================

@app.route("/available")
def available_books():

    books = load_books()

    available = {}


    for book_id, book in books.items():

        if book.get("available"):

            last_return = None


            for item in reversed(book.get("history", [])):

                if item.get("action") == "return":

                    last_return = item

                    break



            available[book_id] = {

                "book": book,

                "last_return": last_return

            }



    return render_template(
        "available.html",
        books=available
    )



# =====================
# RUN
# =====================

if __name__ == "__main__":

    app.run(debug=True)