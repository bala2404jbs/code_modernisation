import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  CircularProgress,
  Button,
  Alert,
} from '@mui/material';
import { Code, Play } from 'lucide-react';
import axios from 'axios';

const ProjectDetails: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [parseMessage, setParseMessage] = useState('');

  const fetchProjectDetails = useCallback(async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project details:', error);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) {
      fetchProjectDetails();
    }
  }, [fetchProjectDetails, projectId]);

  const handleParse = async () => {
    if (!projectId) return;
    
    setParsing(true);
    setParseMessage('');
    
    try {
      console.log('Parsing project:', projectId);
      const response = await axios.post('/api/parse', {
        project_id: projectId
      });
      
      console.log('Parse response:', response.data);
      setProject(response.data);
      setParseMessage('Project parsed successfully!');
    } catch (error: any) {
      console.error('Failed to parse project:', error);
      setParseMessage(error.response?.data?.detail || 'Failed to parse project');
    } finally {
      setParsing(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!project) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Project Not Found
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Project Details
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Code size={24} />
            <Typography variant="h5">{project.project_name}</Typography>
            <Chip 
              label={project.status} 
              color={project.status === 'parsed' ? 'success' : 'warning'}
            />
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" color="text.secondary">
                Source Language
              </Typography>
              <Typography variant="body1" gutterBottom>
                {project.source_language}
                {project.source_framework && ` (${project.source_framework})`}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1" color="text.secondary">
                Project ID
              </Typography>
              <Typography variant="body1" gutterBottom>
                {project.project_id}
              </Typography>
            </Grid>
            {project.description && (
              <Grid item xs={12}>
                <Typography variant="subtitle1" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body1">
                  {project.description}
                </Typography>
              </Grid>
            )}
          </Grid>

          {/* Parse Button */}
          {project.status === 'uploaded' && (
            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                startIcon={<Play />}
                onClick={handleParse}
                disabled={parsing}
              >
                {parsing ? 'Parsing...' : 'Parse Code'}
              </Button>
              {parseMessage && (
                <Alert 
                  severity={parseMessage.includes('successfully') ? 'success' : 'error'}
                  sx={{ mt: 2 }}
                >
                  {parseMessage}
                </Alert>
              )}
            </Box>
          )}

          {project.status === 'parsed' && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success">
                Project has been parsed and is ready for chat and conversion features.
              </Alert>
            </Box>
          )}
        </CardContent>
      </Card>

      <Typography variant="h5" gutterBottom>
        Project Information
      </Typography>
      <Typography variant="body1" color="text.secondary">
        {project.message}
      </Typography>
    </Box>
  );
};

export default ProjectDetails; 