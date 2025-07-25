from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)
api = Api(app)

results = []
student_id_counter = 1

def calculate_average_and_grade(marks):
    avg = sum(marks.values()) / 3
    if avg >= 90:
        grade = 'A'
    elif avg >= 75:
        grade = 'B'
    elif avg >= 60:
        grade = 'C'
    else:
        grade = 'D'
    return avg, grade

def validate_marks(data):
    for subject in ['maths', 'science', 'english']:
        if subject not in data:
            raise BadRequest(f"{subject} mark is required.")
        try:
            mark = float(data[subject])
            if not (0 <= mark <= 100):
                raise ValueError
        except ValueError:
            raise BadRequest(f"{subject} must be a number between 0 and 100.")

class StudentResultList(Resource):
    def get(self):
        return {'students': results}, 200

    def post(self):
        global student_id_counter
        data = request.get_json()

        if not data or 'name' not in data:
            raise BadRequest("Student name is required.")
        
        validate_marks(data)

        marks = {
            'maths': float(data['maths']),
            'science': float(data['science']),
            'english': float(data['english']),
        }

        avg, grade = calculate_average_and_grade(marks)

        student = {
            'id': student_id_counter,
            'name': data['name'],
            'marks': marks,
            'average': avg,
            'grade': grade
        }
        results.append(student)
        student_id_counter += 1

        return {'message': 'Result added successfully', 'student': student}, 201

class StudentResult(Resource):
    def get(self, id):
        student = next((s for s in results if s['id'] == id), None)
        if not student:
            raise NotFound("Student not found.")
        return student, 200

    def put(self, id):
        student = next((s for s in results if s['id'] == id), None)
        if not student:
            raise NotFound("Student not found.")
        
        data = request.get_json()
        if 'name' in data:
            student['name'] = data['name']
        validate_marks(data)

        marks = {
            'maths': float(data['maths']),
            'science': float(data['science']),
            'english': float(data['english']),
        }
        avg, grade = calculate_average_and_grade(marks)

        student['marks'] = marks
        student['average'] = avg
        student['grade'] = grade

        return {'message': 'Result updated successfully', 'student': student}, 200

    def delete(self, id):
        global results
        student = next((s for s in results if s['id'] == id), None)
        if not student:
            raise NotFound("Student not found.")
        results = [s for s in results if s['id'] != id]
        return {'message': f'Student {id} deleted.'}, 200

# Register API endpoints
api.add_resource(StudentResultList, '/results')
api.add_resource(StudentResult, '/results/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
