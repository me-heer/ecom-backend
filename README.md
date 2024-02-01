A sample backend application in FastAPI, Python and MongoDB

### Sample API Calls
#### Get Products
```bash
curl -X GET --location "http://127.0.0.1:8000/products?limit=3&min_price=15&max_price=25" \
    -H "Accept: application/json"
```
#### Create Orders

```bash
curl -X POST --location "http://127.0.0.1:8000/orders" \
    -H "Content-Type: application/json" \
    -d '{
          "items": [
            {"product_id": "65b77503b064d441b7d4c2b7", "bought_quantity": 1}
          ],
          "user_address": {
            "city": "Mumbai",
            "country": "India",
            "zip_code": "12345"
          }
        }'
```

## Future Enhancements
Ideally, I would like to have the following things in a project, but since this was a sample project, I refrained from working on them due to time constraints:
1. Unit/Integration/End-to-end tests
2. When new orders are created, we should be using locks/mutexes or other techniques to prevent race conditions.
3. When the scale of this project grows, use N-tier architecture (Controller -> Service -> Repository)
4. Move MongoDB configurations to its own file
5. Use Pydantic Model Validations instead of manual code
6. Logging
7. Remove `.env` file from the repository (I have just kept it so that anyone can run this)
8. API Documentation (i.e.: Swagger)
9. Authentication/Authorisation (of course)
10. Rate Limiting
11. More Validations
