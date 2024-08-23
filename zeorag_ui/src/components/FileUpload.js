import React, { useState } from 'react';
import { uploadFile } from '../services/api';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (file === null) {
      alert('Please select a file');
    }
    else {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      await uploadFile(formData);
      setFile(null);
      setLoading(false);
      // Show success message to the user
      alert('File uploaded successfully! Reload page to see it in the list.');
    }
  };

  return (
    <div className="container mt-4 file-upload">
      <h3 className="mb-3">Upload a new paper</h3>
      <form onSubmit={handleSubmit} className="d-flex align-items-center">
        <input type="file" onChange={handleFileChange} className="form-control me-2" accept=".pdf"/>
        <button type="submit" className="btn btn-success" disabled={loading}>
          {loading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
      {loading && <div className="text-muted mt-2">Uploading...</div>}
    </div>
  );
};

export default FileUpload;
