from django.http import HttpResponse
from canvasapi import Canvas

# Canvas API URL and API key
API_URL = "https://canvas.instructure.com"
API_KEY = "7~R8JM8yNQYFn34EwfhCRLJZ6RTDaE7HNMnUBVD3NkTMwyXEGG82PEkzzKZNCCBuRf"

# Initialize a Canvas object
canvas = Canvas(API_URL, API_KEY)


def index(request):
    # Retrieve course information from the request, defaulting to 10367017 if not provided
    course_id = request.POST.get("custom_course_id", "10367017")
    course_name = request.POST.get("custom_course_name", "CSEDF24K")

    # Check for missing course information
    if not course_id or not course_name:
        return HttpResponse("Course ID or Course Name is missing.", status=400)

    try:
        # Get course object
        course = canvas.get_course(course_id)

        # Fetch users enrolled in the course with the role of 'student'
        users = course.get_users(enrollment_type=["student"])
        user_list = [(user.id, user.name) for user in users]

        # Fetch assignments for the course
        assignments = course.get_assignments()

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

    result = []

    # Iterate through users and their assignment submission status
    for user_id, user_name in user_list:
        user_assignments = []

        for assignment in assignments:
            submission = assignment.get_submission(user_id)

            # Check if the assignment has been submitted or graded
            submitted = submission.workflow_state in ['submitted', 'graded']

            user_assignments.append({
                'Assignment Name': assignment.name,
                'Submission Status': submitted
            })

        result.append({
            'Student Name': user_name,
            'Assignments': user_assignments
        })

    # Prepare the response text
    response_text = f"List of Students with Their Assignment Status in Course {course_name}:\n\n"

    for user in result:
        response_text += f"Student Name: {user['Student Name']}\nAssignments:\n"
        for assignment in user['Assignments']:
            assignment_name = assignment.get('Assignment Name', 'Name not available')
            submission_status = 'Submitted' if assignment.get('Submission Status', False) else 'Not Submitted'
            response_text += f" - Assignment Name: {assignment_name}\n"
            response_text += f"   Submission Status: {submission_status}\n"
        response_text += "\n"

    return HttpResponse(response_text, content_type="text/plain")
