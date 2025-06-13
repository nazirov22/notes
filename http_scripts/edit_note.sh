curl -X PUT http://localhost:5000/notes/1 \
-H "Content-Type: application/json" \
-d '{"title":"Updated Note","content":"Updated Content","category_id":2,"tags":[1]}'