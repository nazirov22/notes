curl -X POST http://localhost:5000/notes \
-H "Content-Type: application/json" \
-d '{"title":"Test Note","content":"Test Content","user_id":3,"category_id":1,"tags":[1]}'