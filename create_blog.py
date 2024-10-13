import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Thay đổi TEST_BLOG_ID thành ID blog của bạn


# Các phạm vi cần thiết cho Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

class CreatePost:
    creds = None
    # Kiểm tra xem có file token.json không (chứa thông tin xác thực)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Nếu không có hoặc thông tin xác thực không còn hợp lệ, yêu cầu người dùng đăng nhập
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Lưu thông tin xác thực vào file token.json để sử dụng sau này
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    # Tạo Blogger API service
    @staticmethod
    def create_blogger(post, blog_id):
        service = build('blogger', 'v3', credentials=CreatePost.creds)
        # Gửi yêu cầu tạo bài viết
        posts_insert = service.posts().insert(blogId=blog_id, body=post)
        response = posts_insert.execute()
        return response


 # Tạo bài viết mới
#response = create_blogger(service,post)
# post = {
#         'kind': 'blogger#post',
#         'blog': {
#             'id': TEST_BLOG_ID  # ID của blog
#         },
#         'title': 'A test post',
#         'content': '<p>This is a test post with <strong>HTML</strong> content.</p>'
#     }