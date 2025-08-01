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
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import { Settings, Download } from 'lucide-react';
import axios from 'axios';

interface Framework {
  name: string;
  label: string;
  description: string;
}

const CodeConverter: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('');
  const [targetFramework, setTargetFramework] = useState('');
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [converting, setConverting] = useState(false);
  const [conversionResult, setConversionResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects');
      setProjects(response.data.filter((p: any) => p.status === 'parsed'));
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    }
  };

  const fetchFrameworks = async (selectedLanguage: string) => {
    try {
      const response = await axios.get(`/api/frameworks/${selectedLanguage}`);
      setFrameworks(response.data.frameworks);
      setTargetFramework(''); // Reset framework when language changes
    } catch (error) {
      console.error('Failed to fetch frameworks:', error);
      setFrameworks([]);
    }
  };

  const handleTargetLanguageChange = (selectedLanguage: string) => {
    setTargetLanguage(selectedLanguage);
    fetchFrameworks(selectedLanguage);
  };

  const handleConvert = async () => {
    if (!selectedProject || !targetLanguage) {
      setError('Please select a project and target language');
      return;
    }

    setConverting(true);
    setError('');

    try {
      const response = await axios.post('/api/convert', {
        project_id: selectedProject,
        target_language: targetLanguage,
        target_framework: targetFramework,
      });

      setConversionResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Conversion failed');
    } finally {
      setConverting(false);
    }
  };

  const handleDownload = async () => {
    if (!conversionResult) return;
    
    setDownloading(true);
    setError('');

    try {
      const response = await axios.get(`/api/download/${conversionResult.project_id}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `converted_${conversionResult.project_id}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError('Failed to download converted code');
      console.error('Download error:', err);
    } finally {
      setDownloading(false);
    }
  };

  const selectedProjectData = projects.find(p => p.project_id === selectedProject);

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Code Converter
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Select Project and Target Language
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Source Project</InputLabel>
                <Select
                  value={selectedProject}
                  label="Source Project"
                  onChange={(e) => setSelectedProject(e.target.value)}
                >
                  {projects.map((project) => (
                    <MenuItem key={project.project_id} value={project.project_id}>
                      {project.project_name} ({project.source_language})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Target Language</InputLabel>
                <Select
                  value={targetLanguage}
                  label="Target Language"
                  onChange={(e) => handleTargetLanguageChange(e.target.value)}
                >
                  <MenuItem value="python">Python</MenuItem>
                  <MenuItem value="java">Java</MenuItem>
                  <MenuItem value="javascript">JavaScript</MenuItem>
                  <MenuItem value="typescript">TypeScript</MenuItem>
                  <MenuItem value="go">Go</MenuItem>
                  <MenuItem value="rust">Rust</MenuItem>
                  <MenuItem value="php">PHP</MenuItem>
                  <MenuItem value="ruby">Ruby</MenuItem>
                  <MenuItem value="cobol">COBOL</MenuItem>
                  <MenuItem value="cpp">C++</MenuItem>
                  <MenuItem value="c">C</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Target Framework (Optional)</InputLabel>
                <Select
                  value={targetFramework}
                  label="Target Framework (Optional)"
                  onChange={(e) => setTargetFramework(e.target.value)}
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
            </Grid>
          </Grid>

          {selectedProjectData && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Converting from {selectedProjectData.source_language} 
              {selectedProjectData.source_framework && ` (${selectedProjectData.source_framework})`} 
              to {targetLanguage}
              {targetFramework && ` (${targetFramework})`}
            </Alert>
          )}
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {conversionResult && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Conversion Complete
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {conversionResult.message}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Output directory: {conversionResult.output_directory}
            </Typography>
            
            <Button
              variant="outlined"
              startIcon={downloading ? <CircularProgress size={20} /> : <Download />}
              onClick={handleDownload}
              sx={{ mt: 2 }}
              disabled={downloading}
            >
              {downloading ? 'Downloading...' : 'Download Converted Code'}
            </Button>
          </CardContent>
        </Card>
      )}

      <Button
        variant="contained"
        onClick={handleConvert}
        disabled={!selectedProject || !targetLanguage || converting}
        startIcon={converting ? <CircularProgress size={20} /> : <Settings />}
        size="large"
      >
        {converting ? 'Converting...' : 'Convert Code'}
      </Button>
    </Box>
  );
};

export default CodeConverter; 