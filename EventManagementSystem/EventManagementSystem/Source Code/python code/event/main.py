
from flask import Flask, request, render_template, redirect, session, url_for, jsonify
import pymysql
import os.path
from datetime import datetime, timedelta


conn = pymysql.connect(host="localhost", user="root", password="root", db="Event_Hall")
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = "abc"
admin_username = "admin"
admin_password = "admin"


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
pictures = APP_ROOT + "/static/images/"
EventHalls = APP_ROOT + "/static/EventHalls/"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == admin_username and password == admin_password:
        session['role'] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("/message.html", message="Invalid Login Details")


@app.route("/admin_home")
def admin_home():
    return render_template("/admin_home.html")


@app.route("/add_category")
def add_category():
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render_template("add_category.html", categories=categories)


@app.route("/add_category_action", methods=['post'])
def add_category_action():
    category_name = request.form.get("category_name")
    count = cursor.execute("select * from categories where category_name='" + str(category_name) + "'")
    if count > 0:
        return redirect("/category?message=Duplicate Category Name Exist")

    cursor.execute("insert into categories(category_name) value('" + str(category_name)+ "')")
    conn.commit()
    return redirect("/add_category?message1=Category Added successfully")


@app.route("/edit_category")
def edit_category():
    category_id = request.args.get("category_id")
    cursor.execute("select*from categories where category_id='" + str(category_id) + "'")
    categories = cursor.fetchall()
    return render_template("edit_category.html",categories=categories[0],category_id=category_id)


@app.route("/edit_category_action")
def edit_category_action():
    category_id = request.args.get("category_id")
    category_name = request.args.get("category_name")
    cursor.execute("update categories set category_name='" + str(category_name) + "'  where  category_id='" + str(category_id) + "' ")
    conn.commit()
    return redirect("/add_category")




@app.route("/event_organizer_login")
def event_organizer_login():
    return render_template("event_organizer_login.html")


@app.route("/event_organizer_login_action", methods=['post'])
def event_organizer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from event_organizers where email='" + str(email) + "' and password='" + str(password) + "'")
    if count > 0:
        event_organizers = cursor.fetchall()
        if event_organizers[0][6]=='Verified':
            session['event_organizer_id'] = event_organizers[0][0]
            session['role'] = 'event_organizer'
            return redirect("/event_organizer_home")
        else:
            return render_template("message.html", message="Account Not Verified")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/event_organizer_home")
def event_organizer_home():
    return render_template("event_organizer_home.html")


@app.route("/event_organizer_registration")
def event_organizer_registration():
    return render_template("event_organizer_registration.html")

@app.route("/event_organizer_registration_action", methods=['post'])
def event_organizer_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    # picture = request.files.get("picture")
    # path = pictures + "" + picture.filename
    # picture.save(path)
    count = cursor.execute("select * from event_organizers where email='"+str(email)+"' and phone='"+str(phone)+"'")
    if count > 0:
        return redirect("/event_organizer_login?message=Duplicate Details Exist")
    else :
        cursor.execute("insert into event_organizers(name, email, phone, password,address,status) values('"+str(name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(address)+"','Not Verified')")
        conn.commit()
        return redirect("/event_organizer_login?message=Event Organizer Registration Successfully")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_event_halls")
def add_event_halls():
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    cursor.execute("select * from event_halls")
    event_halls = cursor.fetchall()
    return render_template("add_event_halls.html", categories=categories, event_halls=event_halls)


@app.route("/add_event_halls_action", methods=['post'])
def add_event_halls_action():
    event_hall_name = request.form.get("event_hall_name")
    capacity = request.form.get("capacity")
    price_per_hour = request.form.get("price_per_hour")
    about = request.form.get("about")
    category_id = request.form.get("category_id")
    location =  request.form.get("location")
    picture = request.files.get("picture")
    path = EventHalls + "" + picture.filename
    picture.save(path)
    cursor.execute("insert into event_halls(event_hall_name,capacity,price_per_hour,about,category_id,location,picture) values ('" + str(event_hall_name) + "','" + str(capacity) + "','" + str(price_per_hour) + "','" + str(about) + "','" + str(category_id) + "','" + str(location) + "','"+str(picture.filename)+"')")
    conn.commit()
    return redirect("/add_event_halls")


@app.route("/view_event_halls", methods=["GET", "POST"])
def view_event_halls():
    search = request.form.get("search") if request.method == "POST" else None

    if search:
        query = f"""
        SELECT * FROM event_halls 
        WHERE event_hall_name LIKE '%{search}%' 
        OR location LIKE '%{search}%'
        """
        cursor.execute(query)
    else:
        cursor.execute("SELECT * FROM event_halls")

    event_halls = cursor.fetchall()
    return render_template("view_event_halls.html", event_halls=event_halls)

@app.route("/book_event_hall")
def book_event_hall():
    event_hall_id = request.args.get("event_hall_id")
    cursor.execute("SELECT price_per_hour FROM event_halls WHERE event_hall_id=%s", (event_hall_id,))
    price_per_hour = cursor.fetchone()[0]
    return render_template("book_event_hall.html", event_hall_id=event_hall_id, price_per_hour=price_per_hour)


@app.route("/book_event_hall_action", methods=["POST"])
def book_event_hall_action():
    event_hall_id = request.form.get("event_hall_id")
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    from_time = request.form.get("from_time")
    to_time = request.form.get("to_time")
    title = request.form.get("title")
    description = request.form.get("description")
    event_organizer_id = session.get("event_organizer_id")
    booking_date = datetime.now().strftime("%Y-%m-%d")

    # Combine to datetime
    from_datetime = datetime.strptime(from_date + " " + from_time, "%Y-%m-%d %H:%M")
    to_datetime = datetime.strptime(to_date + " " + to_time, "%Y-%m-%d %H:%M")

    if from_datetime >= to_datetime:
        return render_template("message.html", message="Invalid booking time range.")

    # Time collision logic
    cursor.execute("""
        SELECT * FROM event_hall_bookings 
        WHERE event_hall_id = %s AND status!="Payment Pending" and (
            (from_date <= %s AND to_date >= %s)
            AND (from_time <= %s AND to_time >= %s)
        )
    """, (event_hall_id, to_date, from_date, to_time, from_time))

    if cursor.rowcount > 0:
        return render_template("message.html", message="Time slot is already booked.")

    # Get price per hour
    cursor.execute("SELECT price_per_hour FROM event_halls WHERE event_hall_id=%s", (event_hall_id,))
    price_per_hour = float(cursor.fetchone()[0])

    # Calculate total hours
    total_hours = (to_datetime - from_datetime).total_seconds() / 3600
    event_price = round(price_per_hour * total_hours, 2)

    # Insert into bookings
    event_hall_booking = cursor.execute("""
        INSERT INTO event_hall_bookings 
        (booking_date, from_date, to_date, from_time, to_time, event_price, title, description, status, event_organizer_id, event_hall_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Payment Pending', %s, %s)
    """, (
        booking_date, from_date, to_date, from_time, to_time,
        str(event_price), title, description, event_organizer_id, event_hall_id
    ))
    event_hall_booking_id = cursor.lastrowid
    conn.commit()
    return render_template("payment2.html",event_hall_booking_id=event_hall_booking_id,event_price=event_price,float=float)
    # return render_template("message1.html", message=f"Booking Successful! Total Price: ₹{event_price}")


@app.route("/payment_page_action2",methods=['post'])
def payment_page_action2():
    event_hall_booking_id = request.form.get('event_hall_booking_id')
    total_price = request.form.get("total_price")
    cursor.execute("update event_hall_bookings set status='Booked' where event_hall_booking_id='"+str(event_hall_booking_id)+"'")
    conn.commit()
    return render_template("message1.html", message=f"Booking Successful! Total Price: ${total_price}")


@app.route("/user_login")
def user_login():
    return render_template("user_login.html")


@app.route("/user_login_action", methods=['post'])
def user_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from users where email='" + str(email) + "' and password='" + str(password) + "'")
    if count > 0:
        users = cursor.fetchall()
        session['user_id'] = users[0][0]
        session['role'] = 'user'
        return redirect("/user_home")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/user_home")
def user_home():
    return render_template("user_home.html")


@app.route("/user_registration")
def user_registration():
    return render_template("user_registration.html")

@app.route("/user_registration_action", methods=['post'])
def user_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    count = cursor.execute("select * from users where email='"+str(email)+"' and phone='"+str(phone)+"'")
    if count > 0:
        return render_template("message.html",message="Duplicate Details Exist")
        # return redirect("/user_login?message=Duplicate Details Exist")
    else :
        cursor.execute("insert into users(name, email, phone, password,address) values('"+str(name)+"','"+str(email)+"','"+str(phone)+"','"+str(password)+"','"+str(address)+"')")
        conn.commit()
        return render_template("message.html", message="User Registration Successfully")

@app.route("/event_hall_bookings")
def event_hall_bookings():
    query=""
    if session['role'] == 'admin':
        query ="select * from event_hall_bookings where (status='Published' or status='Accepted' or status='Booked')"
    elif session['role']=='event_organizer' :
        query = "select * from event_hall_bookings where event_organizer_id='"+str(session['event_organizer_id'])+"' and (status='Published' or status='Accepted' or status='Booked')"
    cursor.execute(query)
    event_hall_bookings = cursor.fetchall()
    print(event_hall_bookings)
    return render_template("event_hall_bookings.html",event_hall_bookings=event_hall_bookings,get_organizer_by_organizer_id=get_organizer_by_organizer_id,get_event_hall_by_event_hall_id=get_event_hall_by_event_hall_id)

@app.route("/event_hall_bookings_history")
def event_hall_bookings_history():
    if session['role'] == 'admin':
        cursor.execute("select * from event_hall_bookings where status='Rejected'")
    else :
        cursor.execute("select * from event_hall_bookings where event_organizer_id='"+str(session['event_organizer_id'])+"' and status='Rejected'")
    event_hall_bookings = cursor.fetchall()
    return render_template("event_hall_bookings_history.html",event_hall_bookings=event_hall_bookings,get_organizer_by_organizer_id=get_organizer_by_organizer_id,get_event_hall_by_event_hall_id=get_event_hall_by_event_hall_id)




def get_organizer_by_organizer_id(event_organizer_id):
    cursor.execute("select * from event_organizers where event_organizer_id='"+str(event_organizer_id)+"'")
    event_organizer = cursor.fetchone()
    return event_organizer

def get_event_hall_by_event_hall_id(event_hall_id):
    cursor.execute("select * from event_halls where event_hall_id='"+str(event_hall_id)+"'")
    event_hall = cursor.fetchone()
    return event_hall


@app.route("/accept_hall_booking")
def accept_hall_booking():
    event_hall_booking_id = request.args.get("event_hall_booking_id")
    cursor.execute("update event_hall_bookings set status='Accepted' where event_hall_booking_id='" + str(event_hall_booking_id) + "'")
    conn.commit()
    return redirect("/event_hall_bookings")


@app.route("/reject_hall_booking")
def reject_hall_booking():
    event_hall_booking_id = request.args.get("event_hall_booking_id")
    cursor.execute("update event_hall_bookings set status='Rejected' where event_hall_booking_id='" + str(event_hall_booking_id) + "'")
    conn.commit()
    return redirect("/event_hall_bookings")


@app.route("/publish_event")
def publish_event():
    event_hall_booking_id = request.args.get("event_hall_booking_id")
    # cursor.execute("update event_hall_bookings set status='Published' where event_hall_booking_id='" + str(event_hall_booking_id) + "'")
    # conn.commit()
    # cursor.execute("select * from event_hall_bookings where event_hall_booking_id='"+str(event_hall_booking_id)+"'")
    # event_hall_booking= cursor.fetchone()
    # from_date = event_hall_booking[2]
    # to_date = event_hall_booking[3]
    # from_time = event_hall_booking[4]
    # to_time = event_hall_booking[5]
    # status="Published"
    # cursor.execute('insert into ')
    return render_template("publish_event.html",event_hall_booking_id=event_hall_booking_id)

@app.route("/publish_event_action",methods=['post'])
def publish_event_action():
    event_hall_booking_id = request.form.get("event_hall_booking_id")
    cursor.execute("update event_hall_bookings set status='Published' where event_hall_booking_id='" + str(event_hall_booking_id) + "'")
    conn.commit()
    ticket_price = request.form.get("ticket_price")
    cursor.execute("select * from event_hall_bookings where event_hall_booking_id='"+str(event_hall_booking_id)+"'")
    event_hall_booking= cursor.fetchone()
    from_date = event_hall_booking[2]
    to_date = event_hall_booking[3]
    from_time = event_hall_booking[4]
    to_time = event_hall_booking[5]
    title = event_hall_booking[7]
    status="Published"
    description=event_hall_booking[8]
    cursor.execute("insert into events (from_date,to_date,from_time,to_time,title,status,description,event_hall_booking_id,ticket_price) values ('"+str(from_date)+"','"+str(to_date)+"','"+str(from_time)+"','"+str(to_time)+"','"+str(title)+"','"+str(status)+"','"+str(description)+"','"+str(event_hall_booking_id)+"','"+str(ticket_price)+"')")
    conn.commit()

    return render_template("message1.html",message="Event Published")

@app.route("/view_events")
def view_events():
    query=""
    keyword = request.args.get("keyword")
    status = request.args.get("status")
    event_organizer_id = request.args.get("event_organizer_id")
    print(event_organizer_id)

    if event_organizer_id == None:
        event_organizer_id = ""
    if status=='Ongoing':
        if keyword !=None:
           query = "SELECT * FROM events WHERE status = 'Published' and title like '%"+str(keyword)+"%' and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') >= NOW()"
        elif event_organizer_id!="":
            query = "SELECT * FROM events WHERE status = 'Published' and event_hall_booking_id in (select event_hall_booking_id from event_hall_bookings where event_organizer_id='"+str(event_organizer_id)+"') and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') >= NOW()"
        else:
            query = "SELECT * FROM events WHERE status = 'Published' and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') >= NOW()"
    elif status=="Past":
        if keyword != None:
            query = "SELECT * FROM events WHERE status = 'Published' and title like '%" + str(
                keyword) + "%' and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') < NOW()"
        elif event_organizer_id != "":
            query = "SELECT * FROM events WHERE status = 'Published' and event_hall_booking_id in (select event_hall_booking_id from event_hall_bookings where event_organizer_id='" + str(
                event_organizer_id) + "') and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') < NOW()"
        else:
            query = "SELECT * FROM events WHERE status = 'Published' and STR_TO_DATE(CONCAT(to_date, ' ', to_time), '%Y-%m-%d %H:%i') < NOW()"
    cursor.execute(query)
    events = cursor.fetchall()
    cursor.execute("select * from event_organizers")
    event_organizers = cursor.fetchall()
    return render_template("view_events.html",status=status,event_organizers=event_organizers,events=events,get_event_hall_by_event_hall_id=get_event_hall_by_event_hall_id)


@app.route("/book_event_action",methods=['post'])
def book_event_action():
    ticket_price = request.form.get("ticket_price")
    event_id = request.form.get("event_id")

    return render_template("book_event_action.html",ticket_price=ticket_price,event_id=event_id,int=int)


@app.route("/book_event_action1",methods=['post'])
def book_event_action1():
    event_id = request.form.get("event_id")
    ticket_price = request.form.get("ticket_price")
    quantity = request.form.get("quantity")
    ticket_holders = []
    date = datetime.now()
    cursor.execute("insert into bookings (date,status,no_of_tickets,event_id,user_id) values ('"+str(date)+"','Payment Pending','"+str(quantity)+"','"+str(event_id)+"','"+str(session['user_id'])+"')")
    conn.commit()
    booking_id = cursor.lastrowid
    for i in range(1, int(quantity) + 1):
        name = request.form.get(f'name_{i}')
        phone = request.form.get(f'phone_{i}')
        ticket_holders.append({'name': name, 'phone': phone})
        cursor.execute("insert into tickets(name,phone,status,booking_id,ticket_number) values ('"+str(name)+"','"+str(phone)+"','Payment Pending','"+str(booking_id)+"','"+str(i)+"')")
        conn.commit()
    total_price = float(quantity) * float(ticket_price) if float(ticket_price) > 0 else 0
    if total_price==0:
        cursor.execute(
            "update bookings set status='Booked',total_price='" + str(total_price) + "' where booking_id='" + str(
                booking_id) + "'")
        conn.commit()
        cursor.execute("update tickets set status='Booked' where booking_id='" + str(booking_id) + "'")
        conn.commit()
    else:
       return render_template("payment.html",float=float,total_price=total_price,event_id=event_id,booking_id=booking_id)



@app.route("/payment_page_action",methods=['post'])
def payment_page_action():
    booking_id = request.form.get("booking_id")
    total_price = request.form.get("total_price")
    payment_method = request.form.get("payment_method")
    card_holder_name = request.form.get("card_holder_name")
    card_number = request.form.get("card_number")
    expiry_date = request.form.get("expiry_date")
    cvv = request.form.get("cvv")
    cursor.execute("update bookings set status='Booked',total_price='"+str(total_price)+"' where booking_id='"+str(booking_id)+"'")
    conn.commit()
    cursor.execute("update tickets set status='Booked' where booking_id='"+str(booking_id)+"'")
    conn.commit()
    cursor.execute("insert into payment(amount,date,status,cvv,expiry_date,card_number,card_holder_name,card_type,booking_id) values('"+str(total_price)+"','"+str(datetime.now())+"','Payment Successful','"+str(cvv)+"','"+str(expiry_date)+"','"+str(card_number)+"','"+str(card_holder_name)+"','"+str(payment_method)+"','"+str(booking_id)+"')")
    conn.commit()
    return render_template("message1.html",message="Tickets Booked")

@app.route("/view_bookings")
def view_bookings():
    query=""
    if session['role'] == 'user':
         query = "select * from bookings where user_id='"+str(session['user_id'])+"' and (status='Booked' or status='Cancelled')"
    elif session['role']=="event_organizer":
        query = "select * from bookings where (status='Booked' or status='Cancelled') and event_id in(select event_id from events where event_hall_booking_id in (select event_hall_booking_id from event_hall_bookings where status='Published' and event_organizer_id='"+str(session['event_organizer_id'])+"'))"
    elif session['role']=='admin':
        query = "select * from bookings where (status='Booked' or status='Cancelled')"
    cursor.execute(query)
    bookings = cursor.fetchall()
    return render_template("view_bookings.html",getIsReview=getIsReview,float=float,bookings=bookings,get_user_by_user_id=get_user_by_user_id,get_event_by_event_id=get_event_by_event_id)
def get_user_by_user_id(user_id):
    print(user_id)
    cursor.execute("select * from users where user_id='"+str(user_id)+"'")
    user = cursor.fetchone()
    return user

def get_event_by_event_id(event_id):
    cursor.execute("select * from events where event_id='"+str(event_id)+"'")
    events = cursor.fetchone()
    return events


@app.route("/view_tickets")
def view_tickets():
    booking_id = request.args.get("booking_id")
    cursor.execute("select * from tickets where booking_id='"+str(booking_id)+"'")
    tickets = cursor.fetchall()
    return render_template("view_tickets.html",tickets=tickets,booking_id=booking_id)

@app.route("/view_payments")
def view_payments():
    booking_id = request.args.get("booking_id")
    cursor.execute("select * from payment where booking_id='"+str(booking_id)+"'")
    payment = cursor.fetchone()
    return render_template("view_payments.html",payment=payment,get_user_by_user_id2=get_user_by_user_id2)

def get_user_by_user_id2(booking_id):
    cursor.execute("select * from bookings where booking_id='"+str(booking_id)+"'")
    booking = cursor.fetchone()
    user_id = booking[6]
    cursor.execute("select * from users where user_id='"+str(user_id)+"'")
    users = cursor.fetchone()
    return users

@app.route("/give_review")
def give_review():
    event_id = request.args.get("event_id")
    return render_template("give_review.html",event_id=event_id)

@app.route("/give_review_action",methods=['post'])
def give_review_action():
    event_id = request.form.get("event_id")
    rating = request.form.get("rating")
    review = request.form.get("review")
    cursor.execute("insert into reviews (rating,review,event_id,date,user_id) values('"+str(rating)+"','"+str(review)+"','"+str(event_id)+"','"+str(datetime.now())+"','"+str(session['user_id'])+"')")
    conn.commit()
    return render_template("message1.html",message="Review Submitted")

def getIsReview(event_id):
    count = cursor.execute("select * from reviews where event_id='"+str(event_id)+"' and user_id='"+str(session['user_id'])+"'")
    return count

@app.route("/reviews")
def reviews():
    cursor.execute("select * from reviews")
    reviews = cursor.fetchall()
    return render_template("reviews.html",reviews=reviews,get_event_by_event_id=get_event_by_event_id,get_user_by_user_id=get_user_by_user_id)

@app.route("/event_organizers")
def event_organizers():
    cursor.execute("select * from event_organizers")
    event_organizers = cursor.fetchall()
    return render_template("event_organizers.html",event_organizers=event_organizers)

@app.route("/verify_organizer")
def verify_organizer():
    event_organizer_id = request.args.get("event_organizer_id")
    cursor.execute("update event_organizers set status='Verified' where  event_organizer_id='"+str(event_organizer_id)+"'")
    conn.commit()
    return redirect("/event_organizers")


@app.route("/un_verify_organizer")
def un_verify_organizer():
    event_organizer_id = request.args.get("event_organizer_id")
    cursor.execute("update event_organizers set status='Not Verified' where  event_organizer_id='"+str(event_organizer_id)+"'")
    conn.commit()
    return redirect("/event_organizers")

@app.route("/cancel_booking")
def cancel_booking():
    booking_id = request.args.get("booking_id")
    cursor.execute("update bookings set status='Cancelled' where booking_id='"+str(booking_id)+"'")
    conn.commit()
    cursor.execute("update tickets set status='Cancelled' where booking_id='" + str(booking_id) + "'")
    conn.commit()
    return render_template("message1.html",message="Booking Cancelled")

app.run(debug=True,port=80,host="0.0.0.0")
