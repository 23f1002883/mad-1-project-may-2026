from flask import Flask, render_template as rt, request, redirect, url_for, session
from datetime import datetime
from model import *
import os

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ \
os.path.join(current_dir, "Database.sqlite3")

app.config["SECRET_KEY"] = "surper-secret-trekking-key-12345"

db.init_app(app)
app.app_context().push()

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        user = users.query.filter_by(email = user_email).first()

        if user and user_password == user.password:
                session['user_id'] = user.id
                session['user_name'] = user.name

                if user.role == 'admin':
                    return redirect(url_for('admin'))
                elif user.role == 'staff':
                    if user.status == 'pending':
                        session.clear()
                        return "Your account is pending for verification. Please wait for approval."
                    elif user.status == 'blacklisted':
                        session.clear()
                        return "Your account has been deactivated. Access denied."
                    else:
                        return redirect(url_for('staff'))
                else:
                    if user.status == 'blacklisted':
                        session.clear()
                        return "Your account has been deactivated. Access denied."
                    return redirect(url_for('trekker'))
    return rt('homepage.html')


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        contact = request.form.get('contact')
        role = request.form.get('role')

        if not role:
            return "Please select a role before signing up!"
        if role == 'trekker':
            user_status = 'approved'
        else:
            user_status = 'pending'
        
        new_user = users(name = name,
                          email = email,
                            password = password,
                              contact=contact,
                              role = role,
                                status = user_status)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return rt('signup.html')

                
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    total_treks = treks.query.count()
    total_users_staff = users.query.count()
    total_bookings = bookings.query.count()
    
    if request.method == 'POST':
         action = request.form.get('action')
         if action == 'create_trek':
            trek_name = request.form.get('trek_name')
            location = request.form.get('location')
            difficulty = request.form.get('difficulty')
            duration = request.form.get('duration')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            slot = request.form.get('available_slot')
            new_trek = treks(name=trek_name, location=location, 
                            difficulty = difficulty,
                            duration=int(duration) if duration else 1, 
                            start_date = start_date, end_date=end_date,
                            available_slot=int(slot),status='open')    
            db.session.add(new_trek)
            db.session.commit()
            return redirect(url_for('admin'))
        
         elif action == 'edit_trek':
            trek_id = request.form.get('trek_id')
            target_trek = treks.query.filter_by(id=trek_id).first()
            if target_trek:
                target_trek.name = request.form.get('trek_name')
                target_trek.location = request.form.get('location')
                target_trek.difficulty = request.form.get('difficulty')
                target_trek.duration = int(request.form.get('duration'))
                target_trek.start_date = request.form.get('start_date')
                target_trek.end_date = request.form.get('end_date')
                target_trek.available_slot = int(request.form.get('available_slot'))
                db.session.commit()
            return redirect(url_for('admin'))
         
         elif action == 'remove_trek':
            trek_id = request.form.get('trek_id')
            treks.query.filter_by(id=trek_id).delete()
            bookings.query.filter_by(trek_id=trek_id).delete()  
            db.session.commit()
            return redirect(url_for('admin'))

         elif action == 'manage_staff':
            user_id = request.form.get('ID')
            new_status = request.form.get('Status')
            target_user = users.query.filter_by(id=user_id).first()
            if target_user:
                target_user.status = new_status.lower().strip()
                db.session.commit()
            return redirect(url_for('admin'))
        
         elif action == 'assign_staff':
            target_trek_id = request.form.get('trek_id')
            selected_staff_id = request.form.get('staff_id')
            target_trek = treks.query.filter_by(id=target_trek_id).first()
            if target_trek:
                if selected_staff_id:
                    staff_user = users.query.filter_by(id=int(selected_staff_id), role='staff').first()
                    if not staff_user or staff_user.status != 'approved':
                        return redirect(url_for('admin'))
                    
                    target_trek.staff_id = int(selected_staff_id)
                else:
                    target_trek.staff_id = None
                db.session.commit()
            return redirect(url_for('admin'))
         
    search_q = request.args.get('search', '').strip()
    pending_staff = users.query.filter_by(role='staff', status='pending').all()
    approved_staff = users.query.filter_by(role='staff', status='approved').all()
    blacklisted_staff = users.query.filter_by(role='staff', status='blacklisted').all()
    all_trekkers = users.query.filter_by(role='trekker').all()
    all_treks = treks.query.all()
    all_bookings = bookings.query.all()

    if search_q:
        pending_staff = [u for u in pending_staff if search_q.lower() in u.name.lower() or search_q == str(u.id)]
        approved_staff = [u for u in approved_staff if search_q.lower() in u.name.lower() or search_q == str(u.id)]
        blacklisted_staff = [u for u in blacklisted_staff if search_q.lower() in u.name.lower() or search_q == str(u.id)]
        all_trekkers = [u for u in all_trekkers if search_q.lower() in u.name.lower() or search_q == str(u.id)]
        all_treks = [t for t in all_treks if search_q.lower() in t.name.lower() or search_q == str(t.id)]
            
    all_bookings = bookings.query.all()
    return rt('admin.html', pending=pending_staff, approved=approved_staff, 
              blacklisted=blacklisted_staff, all_trekkers=all_trekkers, 
              all_treks=all_treks,all_bookings=all_bookings,
              t_treks=total_treks, t_users_staff=total_users_staff, 
              t_bookings=total_bookings, search_val=search_q)




@app.route('/staff', methods=['GET','POST'])
def staff():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    current_user = users.query.filter_by(id=session['user_id']).first()
    if not current_user or current_user.status == 'blacklisted' or current_user.status == 'pending':
        session.clear()
        return redirect(url_for('home'))

    my_assigned_id = session['user_id']
    my_treks = treks.query.filter_by(staff_id=my_assigned_id).all()
    today_str = datetime.now().strftime('%Y-%m-%d')
    for trek in my_treks:
        if trek.end_date and trek.end_date < today_str:
            trek.status = 'completed'
        elif trek.start_date and trek.start_date <= today_str <= trek.end_date:
            trek.status = 'started'

    if request.method == 'POST':
        action = request.form.get('action')
        trek_id = request.form.get('trek_id')
        target_trek = treks.query.filter_by(id = trek_id, staff_id = my_assigned_id).first()

        if target_trek:
            if action == 'update_slots':
                new_slots = request.form.get('available_slot')
                target_trek.available_slot = int(new_slots)
                db.session.commit()
            elif action == 'change_status':
                new_status = request.form.get('status')
                target_trek.status = new_status
                db.session.commit()
            return redirect(url_for('staff'))
        
    my_treks = treks.query.filter_by(staff_id = my_assigned_id).all()
    all_bookings = bookings.query.all()
    all_users = users.query.all()

    return rt('staff.html', treks_to_guide=my_treks,
              bookings_list=all_bookings, 
              users_list=all_users)



@app.route('/trekker', methods=['GET','POST'])
def trekker():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    current_user_id = session['user_id']
    search_loc = request.args.get('location', '').strip()
    filter_diff = request.args.get('difficulty', '').strip()

    all_open = treks.query.filter_by(status='open').all()
    today_str = datetime.now().strftime('%Y-%m-%d')
    open_itineraries = [t for t in all_open if t.start_date >= today_str]
    
    if search_loc:
        open_itineraries = [t for t in open_itineraries if search_loc.lower() in t.location.lower()]
    if filter_diff:
        open_itineraries = [t for t in open_itineraries if filter_diff.lower() == t.difficulty.lower()]

    user_bookings = bookings.query.filter_by(user_id=current_user_id).all()
    
    active_bookings_data = []
    past_history_data = []
    booked_trek_ids = []

    for b in user_bookings:
        trek_item = treks.query.filter_by(id=b.trek_id).first()
        if trek_item:
            booked_trek_ids.append(b.trek_id)
            
            booking_payload = {
                'trek_id': trek_item.id,
                'name': trek_item.name,
                'location': trek_item.location,
                'start_date': trek_item.start_date,
                'end_date': trek_item.end_date,
                'trek_status': trek_item.status,
                'booking_status': b.status if hasattr(b, 'status') else 'booked'}
            
            if trek_item.status == 'completed' or (trek_item.end_date and trek_item.end_date < today_str):
                past_history_data.append(booking_payload)
            else:
                active_bookings_data.append(booking_payload)

    return rt('trekker.html',
               available_treks=open_itineraries,
               booked_ids=booked_trek_ids,
               current_bookings=active_bookings_data,  
               history=past_history_data,              
               sel_loc=search_loc,
               sel_diff=filter_diff)


@app.route('/book_trek', methods=['POST'])
def book_trek():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    current_user_id = session['user_id']
    target_trek_id = int(request.form.get('trek_id'))
    target_trek = treks.query.filter_by(id=target_trek_id).first()
    current_user = users.query.filter_by(id=current_user_id).first()
    today_str = datetime.now().strftime('%Y-%m-%d')

    if not current_user or current_user.status == 'blacklisted':
        session.clear()
        return redirect(url_for('home'))

    already_booked = bookings.query.filter_by(user_id=current_user_id, trek_id=target_trek_id).first()

    if not already_booked:
        target_trek = treks.query.filter_by(id=target_trek_id).first()
        if target_trek and target_trek.status == 'open' and target_trek.available_slot > 0:
            if target_trek.start_date < today_str:
                return redirect(url_for('trekker'))
            new_booking = bookings(user_id=current_user_id, trek_id=target_trek_id, 
                                   status='booked',booking_date=datetime.now().strftime('%Y-%m-%d %H:%M'))
            db.session.add(new_booking)
            target_trek.available_slot -= 1
            
            if target_trek.available_slot == 0:
                target_trek.status = 'closed'
            
            db.session.commit()
    return redirect(url_for('trekker'))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    current_user = users.query.filter_by(id=session['user_id']).first()
    
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.contact = request.form.get('contact')
        current_user.email = request.form.get('email') 
        db.session.commit()
        session['user_name'] = current_user.name
        return redirect(url_for('trekker'))
        
    return rt('edit_profile.html', user=current_user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    db.create_all()
    app.debug = True
    app.run(host='0.0.0.0')