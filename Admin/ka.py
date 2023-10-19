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
        image_names = []
        for file in files:
            image_names.append(file.filename)
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