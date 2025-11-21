# Todo List Manager - UI

A beautiful and responsive web interface for the Todo List FastAPI backend.

## Features

✨ **Modern Design**
- Gradient header with health status indicator
- Responsive sidebar with real-time statistics
- Smooth animations and transitions
- Mobile-friendly responsive layout

📋 **Todo Management**
- Create new todos with title, description, and priority
- Edit existing todos with modal interface
- Delete individual todos or all at once
- Real-time stats dashboard

🔍 **Advanced Filtering & Search**
- Filter by priority levels (High, Medium, Low)
- Search todos by title or description
- Quick access to all priority categories

📊 **Statistics Dashboard**
- Total todos count
- Count by priority level
- Real-time updates

💾 **Data Management**
- Export todos as JSON file
- Health check indicator
- Empty state handling

## Setup Instructions

### 1. **Ensure FastAPI Backend is Running**

First, start your FastAPI server:

```bash
cd /home/fati/my_projects/FAPIH
source venv/bin/activate
pip install -r requirement.txt
uvicorn todolist_API:app --reload
```

The API should be running on `http://localhost:8000`

### 2. **Serve the UI**

You have several options to serve the UI:

#### Option A: Using Python's built-in server
```bash
cd /home/fati/my_projects/FAPIH/UI
python -m http.server 8080
```
Then open: `http://localhost:8080`

#### Option B: Using Node.js http-server
```bash
npm install -g http-server
cd /home/fati/my_projects/FAPIH/UI
http-server -p 8080
```

#### Option C: Using VS Code Live Server Extension
1. Install "Live Server" extension in VS Code
2. Right-click on `index.html` and select "Open with Live Server"

#### Option D: Using Node.js Express (Recommended)
Create a simple `server.js` in the UI folder:

```javascript
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname)));
app.listen(3000, () => {
    console.log('UI Server running on http://localhost:3000');
});
```

Then run:
```bash
cd /home/fati/my_projects/FAPIH/UI
node server.js
```

### 3. **CORS Configuration (Important)**

If you get CORS errors, update your FastAPI backend to allow the UI origin:

Add to `todolist_API.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## File Structure

```
UI/
├── index.html       # Main HTML structure
├── styles.css       # Responsive styling
├── script.js        # JavaScript functionality
└── README.md        # This file
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## API Endpoints Used

- `GET /` - Welcome message
- `GET /health/` - Health check
- `POST /todos/` - Create todo
- `GET /todos/` - Get all todos
- `GET /todos/{item_id}` - Get single todo
- `PUT /todos/{item_id}` - Update todo
- `DELETE /todos/{item_id}` - Delete todo
- `GET /todos/priority/{priority_level}` - Filter by priority
- `GET /todos/search/?query=` - Search todos
- `GET /todos/stats/` - Get statistics
- `DELETE /todos/` - Delete all todos
- `GET /todos/duplicates/` - Get duplicates
- `POST /todos/duplicate_check/` - Check for duplicates

## Customization

### Change API URL
Edit `script.js` line 3:
```javascript
const API_URL = 'http://your-api-url:port';
```

### Customize Colors
Edit the CSS variables in `styles.css` at the top:
```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... more variables ... */
}
```

### Adjust Responsive Breakpoints
Modify the media queries in `styles.css`:
```css
@media (max-width: 1024px) { /* Tablet */ }
@media (max-width: 768px) { /* Tablet */ }
@media (max-width: 480px) { /* Mobile */ }
```

## Troubleshooting

**Problem: CORS Error**
- Solution: Add CORS middleware to FastAPI backend

**Problem: API Not Responding**
- Solution: Ensure FastAPI is running on port 8000
- Check if API URL is correct in `script.js`

**Problem: Styling Not Loading**
- Solution: Ensure CSS and JS files are in the same directory as HTML
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)

**Problem: Search Not Working**
- Solution: Ensure API database has todos with the search query

## Performance Tips

1. **Production**: Consider minifying CSS/JS files
2. **Caching**: Enable browser caching for static assets
3. **Lazy Loading**: Implement for large todo lists
4. **Compression**: Enable gzip compression on server

## License

This UI is designed to work with the Todo List FastAPI backend.
