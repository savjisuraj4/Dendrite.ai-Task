from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import base64
from bson import ObjectId

app = Flask(__name__)

connection_string = "mongodb+srv://root:root@cluster0.8qywveb.mongodb.net/mydatabase?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client['mydatabase']

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def encode_image(image_path):
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode('utf-8')
    return encoded_image

def decode_image(encoded_image, filename):
    image_data = base64.b64decode(encoded_image)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(save_path, 'wb') as f:
        f.write(image_data)
    return save_path

@app.route('/add-task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    time = request.form.get('time')
    prouser = request.form.get('prouser')
    
    if prouser == "True":
        image_file = request.files['image']
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(filename)
        
        encoded_image = encode_image(filename)
        image_path = encoded_image
    else:
        image_path = None
    
    todo = {
        'title': title,
        'description': description,
        'time': time,
        'prouser': prouser,
        'image_path': image_path
    }
    db.todos.insert_one(todo)
    
    return jsonify({"message": "Task Added Successfully!!", "todo": str(todo)})

def serialize_document(document):
    serialized = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized

@app.route('/get-tasks', methods=['GET'])
def get_todos():
    todos = list(db.todos.find({}))
    serialized_todos = [serialize_document(todo) for todo in todos]
    
    for todo in todos:
        if todo.get('image_path'):
            todo['image_path'] = decode_image(todo['image_path'], todo['title'] + '.jpg')
    
    return jsonify(serialized_todos)

@app.route('/update-task', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description')
    time = request.form.get('time')
    prouser = request.form.get('prouser')
    
    if prouser == "True":
        image_file = request.files['image']
        filename = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(filename)
        
        encoded_image = encode_image(filename)
        image_path = encoded_image
    else:
        image_path = None
    
    update_task = {
        'title': title,
        'description': description,
        'time': time,
        'prouser': prouser,
        'image_path': image_path
    }
    db.todos.update_one({'_id': ObjectId(task_id)}, {'$set': update_task})
    return jsonify({'message': 'Task updated successfully'})

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = request.form.get('task_id')
    message = ""
    
    if task_id:
        db.todos.delete_one({'_id': ObjectId(task_id)})
        message = "Task deleted successfully"
    else:
        message = "Enter Task ID"
    
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)
