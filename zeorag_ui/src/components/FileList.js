import React, { useEffect, useState } from 'react';
import { getFiles } from '../services/api';

const FileList = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await getFiles();
        setFiles(response.data.documents);
      } catch (error) {
        console.error('Error fetching files:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  return (
    <div className="container mt-4">
      <h3 className="mb-3">Papers</h3>
      {loading ? (
        <div className="alert alert-info" role="alert">
          Loading files...
        </div>
      ) : files.length === 0 ? (
        <div className="alert alert-warning" role="alert">
          No files available
        </div>
      ) : (
        <ul className="list-group">
          {files.map((file, index) => (
            <li key={index} className="list-group-item">
              {file}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default FileList;
