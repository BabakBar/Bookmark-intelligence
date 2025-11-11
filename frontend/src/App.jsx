import { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState('');
  const [bookmarks, setBookmarks] = useState([]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/v1/import/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessage(data.message);
      setBookmarks(data.bookmarks);
    } catch (error) {
      setMessage(`An error occurred: ${error.message}`);
    }
  };

  return (
    <>
      <h1 data-testid="main-heading">BookmarkAI</h1>
      <h2>Upload your bookmarks HTML file</h2>
      <div className="card">
        <input data-testid="file-input" type="file" accept=".html" onChange={handleFileChange} />
        <button data-testid="upload-button" onClick={handleUpload}>
          Upload
        </button>
      </div>
      {message && <p data-testid="message">{message}</p>}
      {bookmarks.length > 0 && (
        <div>
          <h3>Parsed Bookmarks:</h3>
          <ul>
            {bookmarks.map((bookmark, index) => (
              <li key={index}>
                <a href={bookmark.url} target="_blank" rel="noopener noreferrer">
                  {bookmark.title}
                </a>
                <span> ({bookmark.folder_path})</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

export default App;
