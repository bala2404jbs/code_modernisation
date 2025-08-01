import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import { Upload, FileArchive } from 'lucide-react';
import axios from 'axios';

const languageOptions = [
  { value: 'java', label: 'Java' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'cobol', label: 'COBOL' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'php', label: 'PHP' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
];

interface Framework {
  name: string;
  label: string;
  description: string;
}

const ProjectUpload: React.FC = () => {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('java');
  const [sourceFramework, setSourceFramework] = useState('');
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const fetchFrameworks = async (selectedLanguage: string) => {
    try {
      const response = await axios.get(`/api/frameworks/${selectedLanguage}`);
      setFrameworks(response.data.frameworks);
      setSourceFramework(''); // Reset framework when language changes
    } catch (error) {
      console.error('Failed to fetch frameworks:', error);
      setFrameworks([]);
    }
  };

  useEffect(() => {
    fetchFrameworks(language);
  }, [language]);

  const handleLanguageChange = (selectedLanguage: string) => {
    setLanguage(selectedLanguage);
    fetchFrameworks(selectedLanguage);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check if file is a zip file
      if (file.type !== 'application/zip' && !file.name.endsWith('.zip')) {
        setError('Please select a ZIP file only');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError('');
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a ZIP file');
      return;
    }

    if (!projectName.trim()) {
      setError('Please enter a project name');
      return;
    }

    setUploading(true);
    setError('');
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('source_language', language);
      formData.append('source_framework', sourceFramework);
      formData.append('description', description);
      formData.append('project_name', projectName);

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        },
      });

      setMessage(`Project uploaded successfully! Project ID: ${response.data.project_id}`);
      setSelectedFile(null);
      setProjectName('');
      setDescription('');
      setSourceFramework('');
      setUploadProgress(0);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Upload Project
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Project Information
          </Typography>
          
          <TextField
            fullWidth
            label="Project Name"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            sx={{ mb: 2 }}
            required
          />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Source Language</InputLabel>
            <Select
              value={language}
              label="Source Language"
              onChange={(e) => handleLanguageChange(e.target.value)}
            >
              {languageOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Source Framework (Optional)</InputLabel>
            <Select
              value={sourceFramework}
              label="Source Framework (Optional)"
              onChange={(e) => setSourceFramework(e.target.value)}
            >
              <MenuItem value="">
                <em>No Framework</em>
              </MenuItem>
              {frameworks.map((framework) => (
                <MenuItem key={framework.name} value={framework.name}>
                  {framework.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Description (Optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
            sx={{ mb: 3 }}
          />

          <Paper
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 3,
              textAlign: 'center',
              mb: 2,
              backgroundColor: selectedFile ? '#f0f8ff' : 'transparent',
            }}
          >
            <input
              accept=".zip"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileSelect}
            />
            <label htmlFor="file-upload">
              <Button
                component="span"
                variant="outlined"
                startIcon={<FileArchive />}
                disabled={uploading}
              >
                Select ZIP File
              </Button>
            </label>
            
            {selectedFile && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Selected: {selectedFile.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </Typography>
              </Box>
            )}
          </Paper>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {message && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {message}
            </Alert>
          )}

          {uploading && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Uploading... {uploadProgress}%
              </Typography>
              <CircularProgress variant="determinate" value={uploadProgress} />
            </Box>
          )}

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : <Upload />}
            size="large"
            fullWidth
          >
            {uploading ? 'Uploading...' : 'Upload Project'}
          </Button>
        </CardContent>
      </Card>

      <Alert severity="info">
        <Typography variant="body2">
          <strong>Note:</strong> Only ZIP files are accepted. Please compress your project files into a ZIP archive before uploading.
          <br />
          <strong>Tip:</strong> If you're on macOS, the system may automatically include metadata folders (like __MACOSX). These will be automatically filtered out during extraction.
        </Typography>
      </Alert>
    </Box>
  );
};

export default ProjectUpload; 