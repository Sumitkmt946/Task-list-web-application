from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend

# In-memory storage (replace with database in production)
tasks = [
    {
        "id": "1",
        "date": "12/03/2019",
        "entityName": "STU Private Limited",
        "taskType": "Call",
        "time": "1:00 PM",
        "contactPerson": "Frodo Baggins",
        "note": "Lorem ipsum dolor sit amet, consectetur adipisc...",
        "status": "Open",
        "phoneNumber": "+1234567890"
    },
    {
        "id": "2",
        "date": "12/03/2019",
        "entityName": "ABC Private Limited",
        "taskType": "Call",
        "time": "1:00 PM",
        "contactPerson": "Sarah Connor",
        "note": "Lorem ipsum dolor sit amet, consectetur adipisc...",
        "status": "Closed",
        "phoneNumber": "+1234567891"
    },
    {
        "id": "3",
        "date": "12/03/2019",
        "entityName": "DEF Private Limited",
        "taskType": "Meeting",
        "time": "2:00 PM",
        "contactPerson": "Peregrin Took",
        "note": "Important client meeting",
        "status": "Open",
        "phoneNumber": "+1234567892"
    }
]

team_members = [
    "Frodo Baggins",
    "Sarah Connor", 
    "Peregrin Took",
    "Sansa Stark",
    "Cersei Lannister",
    "John Doe",
    "Jane Smith",
    "Ned Stark",
    "Jon Snow",
    "Han Solo"
]

# Helper function to find task by ID
def find_task_by_id(task_id):
    return next((task for task in tasks if task["id"] == task_id), None)

# GET /api/tasks - Get all tasks with optional filtering
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        # Get query parameters for filtering
        task_type = request.args.get('taskType')
        status = request.args.get('status')
        contact_person = request.args.get('contactPerson')
        search = request.args.get('search', '').lower()
        
        filtered_tasks = tasks.copy()
        
        # Apply filters
        if task_type and task_type != 'all':
            filtered_tasks = [t for t in filtered_tasks if t['taskType'] == task_type]
            
        if status and status != 'all':
            filtered_tasks = [t for t in filtered_tasks if t['status'] == status]
            
        if contact_person and contact_person != 'all':
            filtered_tasks = [t for t in filtered_tasks if t['contactPerson'] == contact_person]
            
        if search:
            filtered_tasks = [t for t in filtered_tasks if 
                            search in t['entityName'].lower() or 
                            search in t['contactPerson'].lower() or 
                            search in (t['note'] or '').lower()]
        
        return jsonify({
            'success': True,
            'data': filtered_tasks,
            'total': len(filtered_tasks)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# POST /api/tasks - Create new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['entityName', 'taskType', 'time', 'contactPerson']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'{field} is required'
                }), 400
        
        # Create new task
        new_task = {
            'id': str(uuid.uuid4()),
            'date': datetime.now().strftime('%d/%m/%Y'),
            'entityName': data['entityName'],
            'taskType': data['taskType'],
            'time': data['time'],
            'contactPerson': data['contactPerson'],
            'note': data.get('note', ''),
            'status': data.get('status', 'Open'),
            'phoneNumber': data.get('phoneNumber', '')
        }
        
        tasks.append(new_task)
        
        return jsonify({
            'success': True,
            'data': new_task,
            'message': 'Task created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# PUT /api/tasks/<task_id> - Update task
@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = find_task_by_id(task_id)
        if not task:
            return jsonify({
                'success': False, 
                'error': 'Task not found'
            }), 404
        
        data = request.get_json()
        
        # Update task fields
        updatable_fields = ['entityName', 'taskType', 'time', 'contactPerson', 'note', 'status', 'phoneNumber']
        for field in updatable_fields:
            if field in data:
                task[field] = data[field]
        
        return jsonify({
            'success': True,
            'data': task,
            'message': 'Task updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# DELETE /api/tasks/<task_id> - Delete task
@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = find_task_by_id(task_id)
        if not task:
            return jsonify({
                'success': False, 
                'error': 'Task not found'
            }), 404
        
        tasks.remove(task)
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# POST /api/tasks/<task_id>/duplicate - Duplicate task
@app.route('/api/tasks/<task_id>/duplicate', methods=['POST'])
def duplicate_task(task_id):
    try:
        original_task = find_task_by_id(task_id)
        if not original_task:
            return jsonify({
                'success': False, 
                'error': 'Task not found'
            }), 404
        
        # Create duplicate with new ID and current date
        duplicate = original_task.copy()
        duplicate['id'] = str(uuid.uuid4())
        duplicate['date'] = datetime.now().strftime('%d/%m/%Y')
        duplicate['status'] = 'Open'  # Reset status to Open
        
        tasks.append(duplicate)
        
        return jsonify({
            'success': True,
            'data': duplicate,
            'message': 'Task duplicated successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# PATCH /api/tasks/<task_id>/status - Change task status
@app.route('/api/tasks/<task_id>/status', methods=['PATCH'])
def change_task_status(task_id):
    try:
        task = find_task_by_id(task_id)
        if not task:
            return jsonify({
                'success': False, 
                'error': 'Task not found'
            }), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['Open', 'Closed']:
            return jsonify({
                'success': False, 
                'error': 'Invalid status. Must be Open or Closed'
            }), 400
        
        task['status'] = new_status
        
        return jsonify({
            'success': True,
            'data': task,
            'message': f'Task status changed to {new_status}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# GET /api/team-members - Get all team members
@app.route('/api/team-members', methods=['GET'])
def get_team_members():
    try:
        return jsonify({
            'success': True,
            'data': team_members
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Task Management API is running',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Task Management API...")
    print("📋 Available endpoints:")
    print("   GET    /api/tasks - Get all tasks")
    print("   POST   /api/tasks - Create new task")
    print("   PUT    /api/tasks/<id> - Update task")
    print("   DELETE /api/tasks/<id> - Delete task")
    print("   POST   /api/tasks/<id>/duplicate - Duplicate task")
    print("   PATCH  /api/tasks/<id>/status - Change task status")
    print("   GET    /api/team-members - Get team members")
    print("   GET    /api/health - Health check")
    print("\n🌐 Server running on: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)