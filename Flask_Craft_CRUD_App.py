import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crafts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-super-secret-key-for-indikraft'
db = SQLAlchemy(app)

class Craft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    material = db.Column(db.String(100), nullable=True)
    artist_name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    date_created = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return f'<Craft {self.name}>'

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Indikraft Admin</title>
    <style>
        /* A simple, clean, modern style */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            background-color: #f4f7f6;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 960px;
            margin: 20px auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        nav {
            background-color: #004d40; /* Dark teal for Indikraft */
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
            margin: -20px -20px 20px -20px;
        }
        nav a {
            color: #ffffff;
            text-decoration: none;
            padding: 10px 15px;
            font-weight: 500;
            display: inline-block;
        }
        nav a:hover {
            background-color: #00695c;
            border-radius: 4px;
        }
        h1, h2 {
            color: #004d40;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #e0f2f1; /* Light teal */
            color: #004d40;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .action-links a {
            text-decoration: none;
            color: #00796b;
            margin-right: 10px;
        }
        .action-links a.delete {
            color: #d32f2f;
        }
        .btn {
            display: inline-block;
            padding: 10px 15px;
            background-color: #00796b;
            color: #ffffff;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        .btn-primary {
            background-color: #00796b;
        }
        .btn-primary:hover {
            background-color: #00695c;
        }
        .btn-delete {
            background-color: #d32f2f;
        }
        .btn-delete:hover {
            background-color: #c62828;
        }
        .btn-link {
            background: none;
            border: none;
            color: #d32f2f;
            text-decoration: underline;
            cursor: pointer;
            padding: 0;
            font-size: 1em;
        }
        form {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }
        form div {
            display: grid;
            grid-template-columns: 150px 1fr;
            align-items: center;
        }
        form label {
            font-weight: 500;
        }
        form input, form textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box; /* Important for 100% width */
        }
        form textarea {
            min-height: 100px;
            resize: vertical;
        }
        .flash {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-weight: 500;
        }
        .flash-success {
            background-color: #e0f2f1;
            color: #004d40;
            border: 1px solid #b2dfdb;
        }
        .report-card {
            background: #e0f2f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .report-card h3 { margin-top: 0; }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <a href="{{ url_for('index') }}">All Crafts</a>
            <a href="{{ url_for('add_craft') }}">Add New Craft</a>
            <a href="{{ url_for('reports') }}">Reports</a>
        </nav>
        
        <!-- Flash messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="flash flash-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- Content from other templates goes here -->
        {{ content | safe }}
        
    </div>
</body>
</html>
"""
INDEX_TEMPLATE = """
<h1>Craft Inventory</h1>
<table_container>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Artist</th>
                <th>Material</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for craft in crafts %}
            <tr>
                <td>{{ craft.id }}</td>
                <td>{{ craft.name }}</td>
                <td>{{ craft.artist_name }}</td>
                <td>{{ craft.material }}</td>
                <td>₹{{ "%.2f"|format(craft.price) }}</td>
                <td>{{ craft.stock_quantity }}</td>
                <td class="action-links">
                    <a href="{{ url_for('edit_craft', id=craft.id) }}">Edit</a>
                    <!-- The delete action is a small form for security (prevents CSRF) -->
                    <form action="{{ url_for('delete_craft', id=craft.id) }}" method="POST" style="display:inline;">
                        <button type="submit" class="btn-link" onclick="return confirm('Are you sure you want to delete {{ craft.name }}?');">Delete</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7">No crafts found. Add one!</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</table_container>
"""
CRAFT_FORM_TEMPLATE = """
<h1>{{ title }}</h1>
<form method="POST">
    <div>
        <label for="name">Craft Name</label>
        <input type="text" id="name" name="name" value="{{ craft.name if craft else '' }}" required>
    </div>
    <div>
        <label for="artist_name">Artist Name</label>
        <input type="text" id="artist_name" name="artist_name" value="{{ craft.artist_name if craft else '' }}">
    </div>
    <div>
        <label for="material">Materials</label>
        <input type="text" id="material" name="material" value="{{ craft.material if craft else '' }}">
    </div>
    <div>
        <label for="price">Price (₹)</label>
        <input type="number" id="price" name="price" min="0" step="0.01" value="{{ craft.price if craft else 0 }}" required>
    </div>
    <div>
        <label for="stock_quantity">Stock Quantity</label>
        <input type="number" id="stock_quantity" name="stock_quantity" min="0" value="{{ craft.stock_quantity if craft else 0 }}" required>
    </div>
    <div>
        <label for="description">Description</label>
        <textarea id="description" name="description">{{ craft.description if craft else '' }}</textarea>
    </div>
    <div style="grid-template-columns: 150px 1fr;">
        <!-- Empty cell for alignment -->
        <div></div>
        <button type="submit" class="btn btn-primary">{{ 'Update' if craft else 'Create' }} Craft</button>
    </div>
</form>
"""
REPORTS_TEMPLATE = """
<h1>Detailed Reports</h1>

<div class="report-card">
    <h3>Inventory Summary</h3>
    <p><strong>Total Unique Crafts:</strong> {{ summary.total_crafts }}</p>
    <p><strong>Total Stock Value:</strong> ₹{{ "%.2f"|format(summary.total_stock_value) }}</p>
</div>

<h2>Crafts by Material</h2>
{% if summary.by_material %}
    <table>
        <thead>
            <tr>
                <th>Material</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            {% for row in summary.by_material %}
            <tr>
                <td>{{ row[0] or 'N/A' }}</td>
                <td>{{ row[1] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% else %}
    <p>No material data to report.</p>
{% endif %}

<h2>Crafts by Artist</h2>
{% if summary.by_artist %}
    <table>
        <thead>
            <tr>
                <th>Artist</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            {% for row in summary.by_artist %}
            <tr>
                <td>{{ row[0] or 'N/A' }}</td>
                <td>{{ row[1] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% else %}
    <p>No artist data to report.</p>
{% endif %}
"""

@app.route('/')
def index():
    """ (R)ead: Show all crafts on the homepage. """
    all_crafts = Craft.query.order_by(Craft.name).all()
    content = render_template_string(INDEX_TEMPLATE, crafts=all_crafts)
    return render_template_string(LAYOUT_TEMPLATE, title="All Crafts", content=content)

@app.route('/add', methods=['GET', 'POST'])
def add_craft():
    """ (C)reate: Show a form to add a new craft and handle form submission. """
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        description = request.form['description']
        material = request.form['material']
        artist_name = request.form['artist_name']
        price = float(request.form['price'])
        stock_quantity = int(request.form['stock_quantity'])
        
        new_craft = Craft(
            name=name,
            description=description,
            material=material,
            artist_name=artist_name,
            price=price,
            stock_quantity=stock_quantity
        )
        
        db.session.add(new_craft)
        db.session.commit()
        
        flash(f"Craft '{name}' was successfully added!", 'success')
        return redirect(url_for('index'))
    content = render_template_string(CRAFT_FORM_TEMPLATE, craft=None, title="Add New Craft")
    return render_template_string(LAYOUT_TEMPLATE, title="Add New Craft", content=content)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_craft(id):
    """ (U)pdate: Show a form to edit an existing craft. """
  
    craft_to_edit = Craft.query.get_or_404(id)
    
    if request.method == 'POST':
      
        craft_to_edit.name = request.form['name']
        craft_to_edit.description = request.form['description']
        craft_to_edit.material = request.form['material']
        craft_to_edit.artist_name = request.form['artist_name']
        craft_to_edit.price = float(request.form['price'])
        craft_to_edit.stock_quantity = int(request.form['stock_quantity'])
        
      
        db.session.commit()
        
        flash(f"Craft '{craft_to_edit.name}' was successfully updated!", 'success')
        return redirect(url_for('index'))
  
    content = render_template_string(CRAFT_FORM_TEMPLATE, craft=craft_to_edit, title="Edit Craft")
    return render_template_string(LAYOUT_TEMPLATE, title="Edit Craft", content=content)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_craft(id):
    """ (D)elete: Remove a craft from the database. """
   
    craft_to_delete = Craft.query.get_or_404(id)
    craft_name = craft_to_delete.name
    
    db.session.delete(craft_to_delete)
    db.session.commit()
    
    flash(f"Craft '{craft_name}' was successfully deleted.", 'success')
    return redirect(url_for('index'))

@app.route('/reports')
def reports():
    """ "Elite Challenge" Part: Show detailed aggregate reports. """
    
    total_crafts = Craft.query.count()
    
    total_value_query = db.session.query(func.sum(Craft.price * Craft.stock_quantity)).scalar()
    total_stock_value = total_value_query if total_value_query else 0
    
    crafts_by_material = db.session.query(
        Craft.material, 
        func.count(Craft.id)
    ).group_by(Craft.material).order_by(func.count(Craft.id).desc()).all()
    
    crafts_by_artist = db.session.query(
        Craft.artist_name, 
        func.count(Craft.id)
    ).group_by(Craft.artist_name).order_by(func.count(Craft.id).desc()).all()

    summary_data = {
        'total_crafts': total_crafts,
        'total_stock_value': total_stock_value,
        'by_material': crafts_by_material,
        'by_artist': crafts_by_artist
    }
    
    content = render_template_string(REPORTS_TEMPLATE, summary=summary_data)
    return render_template_string(LAYOUT_TEMPLATE, title="Detailed Reports", content=content)


if __name__ == '__main__':
   
    with app.app_context():
        db.create_all()
        
        if Craft.query.count() == 0:
            print("Database is empty. Adding initial dummy data...")
            dummy_crafts = [
                Craft(name="Warli Painting", description="Traditional tribal art", material="Canvas", artist_name="Ramesh L.", price=1500.00, stock_quantity=10),
                Craft(name="Blue Pottery Vase", description="Jaipur Blue Pottery", material="Clay", artist_name="Sita K.", price=2200.00, stock_quantity=5),
                Craft(name="Wooden Elephant", description="Sandalwood carved elephant", material="Wood", artist_name="Arjun S.", price=3500.00, stock_quantity=8),
                Craft(name="Madhubani Silk Scarf", description="Hand-painted silk scarf", material="Silk", artist_name="Priya M.", price=1800.00, stock_quantity=15),
                Craft(name="Terracotta Horse", description="Bankura terracotta horse", material="Clay", artist_name="Sita K.", price=2800.00, stock_quantity=4)
            ]
            db.session.bulk_save_objects(dummy_crafts)
            db.session.commit()
            print("Dummy data added.")

    app.run(debug=True, port=5000)