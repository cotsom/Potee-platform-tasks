db = db.getSiblingDB("shop");
db.createCollection('products');
db.createCollection('users');

db.users.insertMany([
    {
        login: "admin",
        password: "h3g87uh487u43h8f7uh49u3",
        balance: 100,
        available_product: [],
        product_tag: {},
        bank_card_details: 12345678901
    }
]);

db.products.insertMany([
    { 
        product_id: 1, 
        cost: 50, 
        title: 'krysa', 
        description: 'Krysa',
        link: 'https://spinningrat.online/'
    },
    { 
        product_id: 2, 
        cost: 50, 
        title: 'rick', 
        description: 'Rick',
        link: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' 
    },
    { 
        product_id: 3, 
        cost: 300, 
        title: 'flag', 
        description: 'flag' 
    },
    { 
        product_id: 4, 
        cost: 90, 
        title: 'guest-ticket', 
        description: 'Guest ticket' 
    },
    { 
        product_id: 5, 
        cost: 100, 
        title: 'speaker-ticket', 
        description: 'Speaker ticket' 
    }
]);

