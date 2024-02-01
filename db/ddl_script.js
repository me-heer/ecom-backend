// Create products collection
db.createCollection("products");

// Define indexes
db.products.createIndex({ "product_name": 1 }, { unique: true });
db.products.createIndex({ "product_price": 1 });
db.products.createIndex({ "product_quantity": 1 });
