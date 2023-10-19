from flask import Flask,render_template,request,url_for,redirect
from pymongo import MongoClient
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import gridfs
from email.message import EmailMessage
import ssl
import smtplib
from datetime import date
from pymongo import errors









app = Flask(__name__)

# client = MongoClient('localhost', 27017)
# app.config['MONGO_URI']='mongodb://localhost:27017'
# mongo=PyMongo(app)
client = MongoClient("mongodb+srv://MrAlumni:iitisoc123@alumniportal.g0c22w7.mongodb.net/admin")

db = client["Alumni"]
EVENTS = db.Events
MAILS=db.Mails
FORUMS=db.Forums
fs=gridfs.GridFS(db)



@app.route('/')
def hello():
    return render_template('home.html')


#---------------------------EVENTS---------------------------------

@app.route('/eventsext', methods=('GET', 'POST'))
def eventsext():
    if request.method=='POST':
        event_name = request.form['event_name']
        schedule = request.form['schedule']
        description = request.form['description']
        EVENTS.insert_one({'event_name': event_name, 'schedule': schedule, 'description':description})
        return redirect(url_for('events'))
    return render_template('eventsext.html')

@app.post('/events/<id>/delete/')
def delete(id):
    # eventtobedeleted={'_id':ObjectId(id)}
    EVENTS.delete_one({"_id":ObjectId(id)})
    # events.delete_one(eventtobedeleted)
    return redirect(url_for('events'))


@app.route('/events')
def events():
    all_events = EVENTS.find()
    return render_template('events.html', events=all_events)







# --------------------------------------GALLERY--------------

@app.route('/galleryext', methods=('GET', 'POST'))
def gallerysext():
    if request.method=='POST':
        event_gallery_name = request.form['event_gallery_name']
        image_file = request.files['gallery_image']
        file_data=image_file.read()
        fs.put(file_data,filename=event_gallery_name)
        return redirect(url_for('gallerydisplay'))
    return render_template('galleryext.html')

@app.route('/gallery')
def gallerydisplay():
    try:
        # Retrieve all image files from GridFS
        files = fs.find()
        image_names = [file.filename for file in files]

        # Sort the image names alphabetically
        image_names = sorted(image_names)

        return render_template('gallery.html', image_names=image_names)
    except errors.ServerSelectionTimeoutError:
        return 'Failed to connect to MongoDB server'
@app.route('/display/<filename>')
def display_image(filename):
    try:
        # Retrieve the image from GridFS by filename
        file = fs.find_one({'filename': filename})
        if file is None:
            return 'Image not found'
        else:
            # Set the content type and return the image data
            response = app.response_class(file.read(), mimetype='image/jpeg')
            return response
    except errors.ServerSelectionTimeoutError:
        return 'Failed to connect to MongoDB server'

@app.route('/delete/<filename>', methods=['POST'])
def delete_image(filename):
    try:
        # Find the image by filename
        file = fs.find_one({'filename': filename})
        if file is None:
            return 'Image not found'
        else:
            # Delete the image from GridFS
            fs.delete(file._id)
            return redirect(url_for('gallerydisplay'))
    except errors.ServerSelectionTimeoutError:
        return 'Failed to connect to MongoDB server'






# --------------------------MAILS----------------------------------------
@app.route('/mail')
def mail():
    all_mails=MAILS.find()
    return render_template('mail.html',mails=all_mails)

@app.route('/mailsext', methods=['GET','POST'])
def mailsext():
    email_sender='mralumniportal@gmail.com'
    email_password='iitisoc123'   
    if request.method=='POST':
        email_receiver=request.form['email']
        subject=request.form['subject']
        body=request.form['message']
        today=date.today()
        today_string = today.strftime("%Y-%m-%d")


        MAILS.insert_one({'to': email_receiver, 'subject': subject, 'body':body,'date':today_string})

        em=EmailMessage()
        em['From']=email_sender
        em['To']=email_receiver
        em['Subject']=subject
        em.set_content(body)

        context=ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        return redirect(url_for('mail'))
    return render_template('mailsext.html')









# --------------------------------FORUMS------------------------


@app.route('/forumsext', methods=('GET', 'POST'))
def forumsext():
    if request.method=='POST':
        alumni_name = request.form['alumni_name']
        batch = request.form['batch']
        comment = request.form['comment']
        FORUMS.insert_one({'alumni_name': alumni_name, 'batch': batch, 'comment':comment})
        return redirect(url_for('forums'))
    return render_template('forumsext.html')

@app.post('/forums/<id>/delete/')
def delete_forum(id):
    # eventtobedeleted={'_id':ObjectId(id)}
    FORUMS.delete_one({"_id":ObjectId(id)})
    # events.delete_one(eventtobedeleted)
    return redirect(url_for('forums'))


@app.route('/forums')
def forums():
    all_forumss = FORUMS.find()
    return render_template('forums.html', forumss=all_forumss)





if __name__=="__main__":
    app.run(debug=True)
