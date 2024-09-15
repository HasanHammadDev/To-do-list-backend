# Todo List Backend

Please refer to the [To do list frontend] repository for the frontend code, which is located here:

https://github.com/HasanHammadDev/To-do-list-frontend
## Installation

How to install
```bash 
  git clone https://github.com/HasanHammadDev/To-do-list-backend.git
  cd To-do-list-backend
  python -m venv venv
  source venv/scripts/activate
  pip install -r requirements.txt
  flask run
```
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file in the root of your Todo List Backend folder.

`DATABASE_URI`=your_db_uri
`JWT_SECRET_KEY`=your_jwt_secret_key
`SECRET_KEY`=your_secret_key
