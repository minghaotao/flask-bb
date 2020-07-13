import requests
import json
from os import sep
import sys


class Blackboard(object):
    def __init__(self, cred=None, token=None):

        learn_urls = {
            'Staging': 'bb_url',
            'Production': 'bb_url'
        }

        self.server_url = learn_urls['Staging']

        if cred:
            self.cred = cred
        else:
            self.get_ced()
        if token:
            self.token = token
        else:
            self.get_token()

        self.headers = {'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(self.token['access_token'])}

    def full_path(self, file_name):
        return f'{sys.path[0]}{sep}{file_name}'

    def get_ced(self):
        with open('/Users/edwardt/Desktop/Flask_web/Flask_bb/flaskbb/Bb_API/keys.json', 'r') as f:
            cred = json.load(f)
        self.cred = cred

    def get_token(self):
        token_url = '{}/learn/api/public/v1/oauth2/token'.format(self.server_url)
        token_data = {'grant_type': 'client_credentials'}
        r = requests.post(token_url, auth=(self.cred['application_key'], self.cred['secret']), data=token_data)
        if r.status_code == 200:
            self.token = json.loads(r.text)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def get_courses(self):
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {}'.format(self.token['access_token'])}
        course_api_url = '{}/learn/api/public/v1/courses'.format(self.server_url)
        r = requests.get(course_api_url, headers=headers)
        if r.status_code == 200:
            json_data = r.json()
            for results in json_data["results"]:
                print(results['courseId'], results['name'], results['enrollment']['type'])
        else:
            raise Exception('Error when getting courses, http status {}: {}'.format(r.status_code, r.text))

    def get_users(self):

        users = '{url}/learn/api/public/v1/users'.format(url=self.server_url)

        r = requests.get(users, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def get_institution_roles(self):
        in_roles = '{url}/learn/api/public/v1/institutionRoles'.format(url=self.server_url)
        r = requests.get(in_roles, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def create_user(self, username):
        payload = {
            "externalId": username,
            "dataSourceId": "_2_1",
            "userName": username,
            "password": username,
            "systemRoleIds": [
                "User"
            ],
            "availability": {
                "available": "Yes"
            },
            "name": {
                "given": "Students",
                "family": ",
            }

        }
        create_user = '{url}/learn/api/public/v1/users'.format(url=self.server_url)
        r = requests.post(create_user, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return json.dumps(r.json(), indent=4)
        else:
            # raise Exception('The error message is {}:{}'.format(r.status_code, r.text))
            pass

    def get_courseid(self, courseId):

        courseid = '{url}/learn/api/public/v1/courses/courseId:{courseId}'.format(url=self.server_url,
                                                                                  courseId=courseId)
        r = requests.get(courseid, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('the error message is {}:{}'.format(r.status_code, r.text))

    def create_course(self, courseId, courseName, bloom, term=None):

        payload = {
            "courseId": courseId,
            "name": courseName,
            "organization": bloom,
            # "termId": f"externalId:{term}",
            "availability": {
                "available": "Yes",
            }

        }

        options = [{"termId": f"externalId:{term}"}]
        if term is not None:
            payload.update(options[0])
            print(payload)

        course = '{url}/learn/api/public/v2/courses'.format(url=self.server_url)
        r = requests.post(course, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def get_course_memberships(self):
        userId = 'userName:m_tao'
        courseM_api = '{url}/learn/api/public/v1/users/{userId}/courses'.format(url=self.server_url, userId=userId)
        r = requests.get(courseM_api, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('the error message is {}:{}'.format(r.status_code, r.text))

    def get_course_enrollment(self, courseId):
        courseE_api = '{url}/learn/api/public/v1/courses/{courseId}/users'.format(url=self.server_url,
                                                                                  courseId=courseId)
        r = requests.get(courseE_api, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('the error message is {}:{}'.format(r.status_code, r.text))

    def get_user_enroolment(self):
        userId = 'userName:tlkiley'
        courseId = 'courseId:TEEL230_VG_F2018'
        courseM_api = '{url}/learn/api/public/v1/courses/{courseId}/users/{userId}'.format(url=self.server_url,
                                                                                           userId=userId,
                                                                                           courseId=courseId)
        r = requests.get(courseM_api, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('the error message is {}:{}'.format(r.status_code, r.text))

    def create_course_memberships(self, course, user_id, role):

        payload = {
            "availability": {
                "available": "Yes"
            },
            "courseRoleId": role
        }

        create_courseMembership = '{url}/learn/api/public/v1/courses/{courseId}/users/{userId}'.format(
            url=self.server_url,
            courseId=course,
            userId=user_id)
        r = requests.put(create_courseMembership, data=json.dumps(payload), headers=self.headers)

        if r.status_code == 201:
            return "Users has been added course as an instructor"

        elif r.status_code == 409:
            pass
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def get_data_sources(self, source_id):

        data_source = '{url}/learn/api/public/v1/dataSources/{dataSourceId}'.format(url=self.server_url,
                                                                                    dataSourceId=source_id)
        r = requests.get(data_source, headers=self.headers)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def update_course(self, course_id, term):

        payload = {

            "termId": term,

        }

        update_course = '{url}/learn/api/public/v2/courses/courseId:{courseId}'.format(url=self.server_url,
                                                                                       courseId=course_id)
        r = requests.patch(update_course, data=json.dumps(payload), headers=self.headers)

        if r.status_code == 200:
            return "Course has updated"
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def get_terms(self):

        get_terms = '{url}/learn/api/public/v1/terms'.format(url=self.server_url)

        r = requests.get(get_terms, headers=self.headers)

        if r.status_code == 200:
            return json.dumps(r.json(), indent=4)
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def course_copy(self, s_course, d_course, status):

        payload = {
            "targetCourse": {
                # # "courseId": d_course,
                # "id": d_course
            },
            "copy": {
                "adaptiveReleaseRules": True,
                "announcements": True,
                "assessments": True,
                "blogs": True,
                "calendar": True,
                "contacts": True,
                "contentAlignments": True,
                "contentAreas": True,
                "discussions": 'ForumsOnly',
                "gradebook": True,
                "groupSettings": True,
                "journals": True,
                "retentionRules": True,
                "rubrics": True,
                "settings": {
                    "availability": True,
                    "bannerImage": True,
                    "duration": True,
                    "enrollmentOptions": False,
                    "guestAccess": False,
                    "languagePack": True,
                    "navigationSettings": True,
                    "observerAccess": False
                },
                "tasks": True,
                "wikis": True
            }
        }

        options = [{"courseId": d_course}, {"id": d_course}]
        # CourseID will copy to the new course shell (status is 1)
        # ID will copy it to the exsiting course and it will only take primary key (status is 0)
        if status == 1:
            payload["targetCourse"].update(options[0])
            print(payload["targetCourse"])
        elif status == 0:
            payload["targetCourse"].update(options[1])
            print(payload["targetCourse"])

        cousecopy = '{url}/learn/api/public/v2/courses/courseId:{courseId}/copy'.format(url=self.server_url,
                                                                                        courseId=s_course)
        r = requests.post(cousecopy, data=json.dumps(payload), headers=self.headers)

        if r.status_code == 202:
            return "Course copy has completed"
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))

    def course_merge(self, p_courseid, c_courseid):

        payload = {
            "ignoreEnrollmentErrors": 'ture'

        }
        course_merege = '{url}/learn/api/public/v1/courses/courseId:{courseId}/children/courseId:{childCourseId}'.format(
            url=self.server_url,
            courseId=p_courseid,
            childCourseId=c_courseid)
        r = requests.put(course_merege, data=json.dumps(payload), headers=self.headers)

        if r.status_code == 201:
            return "course has been merged"
        else:
            raise Exception('The error message is {}:{}'.format(r.status_code, r.text))


if __name__ == '__main__':
    bb = Blackboard()
#     # print(bb.get_institution_roles())
#     # print(bb.get_users())
#     print(bb.get_courseid('courseId:TEST'))

